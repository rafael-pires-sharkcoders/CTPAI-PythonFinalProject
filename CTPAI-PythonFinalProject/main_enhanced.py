#!/usr/bin/env python3
"""
Enhanced Object Detection System - Main Application

A comprehensive real-time object detection system using YOLOv8 with advanced features:
- Configurable YAML-based settings
- Advanced error handling and logging
- Performance monitoring and metrics
- Video recording capabilities
- CLI interface with rich output
- Thread-safe operations
- Resource monitoring

Usage:
    python main_enhanced.py [OPTIONS]

Author: Enhanced Object Detection System v3.0
"""

import sys
import signal
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any
import argparse

import cv2
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich import print as rprint

# Import our enhanced modules
from core.config import get_config, Config
from core.logging import setup_logging, get_logger
from core.camera import CameraManager, CameraError
from core.state import StateManager, AppState
from detector.enhanced_detector import EnhancedYOLODetector, DetectorError
from ui.display import InterfaceDrawer

console = Console()
logger = get_logger(__name__)


class EnhancedObjectDetectorApp:
    """
    Enhanced Object Detection Application with comprehensive features.
    
    Features:
    - Advanced error handling and recovery
    - Performance monitoring and statistics
    - Video recording with configurable settings
    - Thread-safe operation with proper resource management
    - CLI interface with rich terminal output
    - Configurable via YAML files
    - Comprehensive logging system
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the enhanced application."""
        # Load configuration
        if config_path:
            from core.config import ConfigManager
            config_manager = ConfigManager(config_path)
            self.config = config_manager.load_config()
        else:
            self.config = get_config()
        
        # Initialize logging
        setup_logging()
        logger.info("Enhanced Object Detection System starting...")
        
        # Core components
        self.state_manager = StateManager()
        self.camera_manager: Optional[CameraManager] = None
        self.detector: Optional[EnhancedYOLODetector] = None
        self.ui_drawer: Optional[InterfaceDrawer] = None
        
        # Video recording
        self.video_writer: Optional[cv2.VideoWriter] = None
        self.recording_path: Optional[Path] = None
        
        # Threading
        self.main_thread: Optional[threading.Thread] = None
        self.shutdown_event = threading.Event()
        
        # Statistics
        self.app_start_time = time.time()
        self.frames_processed = 0
        self.last_screenshot_time = 0
        
        # Display state
        self.fullscreen = self.config.display.fullscreen
        
        # Rich console for status updates
        self.live_display: Optional[Live] = None
        
        logger.info("Application initialized successfully")
    
    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self.shutdown()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def initialize_components(self) -> bool:
        """Initialize all application components."""
        try:
            # Initialize state manager
            self.state_manager.set_state(AppState.INITIALIZING)
            
            # Initialize UI drawer
            self.ui_drawer = InterfaceDrawer(self.config)
            logger.info("UI drawer initialized")
            
            # Initialize camera
            self.camera_manager = CameraManager(self.config)
            if not self.camera_manager.initialize_camera():
                raise CameraError("Failed to initialize camera")
            
            logger.info("Camera initialized successfully")
            
            # Initialize detector
            self.detector = EnhancedYOLODetector(self.config)
            logger.info("Detector initialized successfully")
            
            # Setup recording directory
            if self.config.recording.enabled:
                recording_dir = Path(self.config.recording.output_dir)
                recording_dir.mkdir(exist_ok=True)
                logger.info(f"Recording directory: {recording_dir}")
            
            return True
            
        except Exception as e:
            logger.error(f"Component initialization failed: {e}")
            self.state_manager.error(str(e))
            return False
    
    def start_camera_capture(self) -> bool:
        """Start camera capture in separate thread."""
        try:
            if not self.camera_manager.start_capture():
                raise CameraError("Failed to start camera capture")
            
            logger.info("Camera capture started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start camera capture: {e}")
            return False
    
    def process_frame(self, frame: np.ndarray, frame_time: float) -> Optional[np.ndarray]:
        """
        Process a single frame through the detection pipeline.
        
        Args:
            frame: Input frame
            frame_time: Frame timestamp
            
        Returns:
            Processed frame with overlays or None if processing failed
        """
        try:
            # Skip processing if paused
            if self.state_manager.is_paused:
                return frame
            
            # Apply frame skipping for performance
            if (self.frames_processed % (self.config.performance.skip_frames + 1)) != 0:
                self.frames_processed += 1
                return frame
            
            # Create copy for processing
            processed_frame = frame.copy()
            
            # Detect objects
            detections = self.detector.detect_objects(frame)
            
            # Update statistics
            self.state_manager.increment_detections(len(detections))
            self.state_manager.update_frame_count()
            
            # Draw detections
            if detections:
                self.ui_drawer.draw_detections(processed_frame, detections)
            
            # Draw UI elements
            self._draw_ui_overlay(processed_frame)
            
            # Record frame if recording
            if self.state_manager.is_recording and self.video_writer:
                self.video_writer.write(processed_frame)
            
            self.frames_processed += 1
            return processed_frame
            
        except Exception as e:
            logger.error(f"Frame processing error: {e}")
            return frame
    
    def _draw_ui_overlay(self, frame: np.ndarray) -> None:
        """Draw UI overlay on frame."""
        try:
            # Performance metrics
            perf = self.state_manager.performance
            
            # FPS
            if self.config.display.show_fps:
                self.ui_drawer.draw_fps(frame, perf.fps)
            
            # Detection count
            if self.config.display.show_detection_count:
                detection_count = len(self.detector.get_performance_stats().get('recent_detections', []))
                self.ui_drawer.draw_detection_count(frame, detection_count)
            
            # Performance info
            if self.state_manager.show_performance:
                detector_stats = self.detector.get_performance_stats()
                system_stats = self.detector.get_system_info()
                
                combined_stats = {**detector_stats, **system_stats}
                self.ui_drawer.draw_performance_info(frame, combined_stats)
            
            # Status messages
            if self.state_manager.is_paused:
                self.ui_drawer.draw_status_message(
                    frame, "PAUSED - Press SPACE to continue", (0, 0, 255)
                )
            
            # Recording indicator
            if self.state_manager.is_recording:
                self.ui_drawer.draw_recording_indicator(frame)
            
        except Exception as e:
            logger.debug(f"UI overlay error: {e}")
    
    def handle_key_input(self, key: int) -> bool:
        """
        Handle keyboard input.
        
        Args:
            key: Key code
            
        Returns:
            True to continue, False to exit
        """
        try:
            # Convert key to character
            key_char = chr(key) if 0 <= key <= 127 else None
            
            # Exit keys
            if (key_char and key_char.lower() in self.config.controls.exit_keys) or key == 27:
                logger.info("Exit key pressed")
                return False
            
            # Pause/resume
            elif key_char == self.config.controls.pause_key:
                self.state_manager.toggle_pause()
                status = "Paused" if self.state_manager.is_paused else "Resumed"
                rprint(f"[yellow]🎬 {status}[/yellow]")
            
            # Reset statistics
            elif key_char == self.config.controls.reset_key:
                self.state_manager.reset_performance()
                if self.detector:
                    self.detector.reset_stats()
                rprint("[green]📊 Statistics reset[/green]")
            
            # Toggle performance display
            elif key_char == self.config.controls.performance_toggle_key:
                self.state_manager.toggle_performance_display()
                status = "enabled" if self.state_manager.show_performance else "disabled"
                rprint(f"[blue]📈 Performance display {status}[/blue]")
            
            # Screenshot
            elif key_char == self.config.controls.screenshot_key:
                self._take_screenshot()
            
            # Recording toggle
            elif key_char == self.config.controls.record_toggle_key:
                self._toggle_recording()
            
            # Fullscreen toggle
            elif key_char == self.config.controls.fullscreen_toggle_key:
                self._toggle_fullscreen()
            
            return True
            
        except Exception as e:
            logger.error(f"Key handling error: {e}")
            return True
    
    def _take_screenshot(self) -> None:
        """Take a screenshot of current frame."""
        try:
            current_time = time.time()
            
            # Rate limiting (max 1 screenshot per second)
            if current_time - self.last_screenshot_time < 1.0:
                return
            
            # Get latest frame
            frame_data = self.camera_manager.get_frame(timeout=0.1)
            if not frame_data:
                rprint("[red]❌ No frame available for screenshot[/red]")
                return
            
            frame, _ = frame_data
            
            # Generate filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.jpg"
            filepath = Path(filename)
            
            # Save screenshot
            if cv2.imwrite(str(filepath), frame):
                self.last_screenshot_time = current_time
                rprint(f"[green]📸 Screenshot saved: {filename}[/green]")
            else:
                rprint("[red]❌ Failed to save screenshot[/red]")
                
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            rprint("[red]❌ Screenshot failed[/red]")
    
    def _toggle_recording(self) -> None:
        """Toggle video recording."""
        try:
            if not self.config.recording.enabled:
                rprint("[yellow]⚠️ Recording is disabled in configuration[/yellow]")
                return
            
            if self.state_manager.is_recording:
                self._stop_recording()
            else:
                self._start_recording()
                
        except Exception as e:
            logger.error(f"Recording toggle error: {e}")
            rprint("[red]❌ Recording toggle failed[/red]")
    
    def _start_recording(self) -> None:
        """Start video recording."""
        try:
            if self.video_writer:
                return  # Already recording
            
            # Generate filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}{self.config.recording.extension}"
            self.recording_path = Path(self.config.recording.output_dir) / filename
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*self.config.recording.codec)
            frame_size = (self.config.camera.width, self.config.camera.height)
            
            self.video_writer = cv2.VideoWriter(
                str(self.recording_path),
                fourcc,
                self.config.recording.fps,
                frame_size
            )
            
            if self.video_writer.isOpened():
                self.state_manager.start_recording()
                rprint(f"[green]🎥 Recording started: {filename}[/green]")
            else:
                self.video_writer = None
                rprint("[red]❌ Failed to start recording[/red]")
                
        except Exception as e:
            logger.error(f"Recording start error: {e}")
            rprint("[red]❌ Failed to start recording[/red]")
    
    def _stop_recording(self) -> None:
        """Stop video recording."""
        try:
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
                
                self.state_manager.stop_recording()
                
                if self.recording_path and self.recording_path.exists():
                    file_size = self.recording_path.stat().st_size / (1024 * 1024)  # MB
                    rprint(f"[green]🎥 Recording saved: {self.recording_path.name} ({file_size:.1f}MB)[/green]")
                else:
                    rprint("[yellow]⚠️ Recording stopped but file not found[/yellow]")
                
        except Exception as e:
            logger.error(f"Recording stop error: {e}")
            rprint("[red]❌ Failed to stop recording[/red]")
    
    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        try:
            # Initialize fullscreen state if not exists
            if not hasattr(self, 'fullscreen'):
                self.fullscreen = self.config.display.fullscreen
            
            self.fullscreen = not self.fullscreen
            
            if self.fullscreen:
                # Enable fullscreen
                cv2.namedWindow(self.config.display.window_name, cv2.WINDOW_NORMAL)
                cv2.setWindowProperty(
                    self.config.display.window_name, 
                    cv2.WND_PROP_FULLSCREEN, 
                    cv2.WINDOW_FULLSCREEN
                )
                rprint("[green]🖥️ Fullscreen mode ENABLED[/green] (Press F to exit)")
            else:
                # Return to windowed mode
                cv2.setWindowProperty(
                    self.config.display.window_name, 
                    cv2.WND_PROP_FULLSCREEN, 
                    cv2.WINDOW_NORMAL
                )
                cv2.resizeWindow(self.config.display.window_name, 1024, 768)
                rprint("[cyan]🪟 Windowed mode ENABLED[/cyan]")
                
        except Exception as e:
            logger.error(f"Fullscreen toggle error: {e}")
            rprint("[red]❌ Failed to toggle fullscreen[/red]")
    
    def create_status_table(self) -> Table:
        """Create status table for live display."""
        table = Table(title="Object Detection System Status")
        
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        # State
        state_color = "green" if self.state_manager.is_running else "yellow"
        table.add_row("State", f"[{state_color}]{self.state_manager.state.value.title()}[/{state_color}]")
        
        # Performance
        perf = self.state_manager.performance
        table.add_row("FPS", f"{perf.fps:.1f}")
        table.add_row("Total Detections", str(perf.total_detections))
        table.add_row("Frames Processed", str(self.frames_processed))
        
        # System info
        if self.detector:
            system_info = self.detector.get_system_info()
            if 'memory_usage_mb' in system_info:
                table.add_row("Memory Usage", f"{system_info['memory_usage_mb']:.1f} MB")
            if 'system_cpu_percent' in system_info:
                table.add_row("CPU Usage", f"{system_info['system_cpu_percent']:.1f}%")
        
        # Recording status
        recording_status = "🔴 Recording" if self.state_manager.is_recording else "⚫ Not Recording"
        table.add_row("Recording", recording_status)
        
        # Uptime
        uptime = time.time() - self.app_start_time
        table.add_row("Uptime", f"{uptime:.0f}s")
        
        return table
    
    def print_startup_info(self) -> None:
        """Print startup information."""
        startup_panel = Panel(
            f"""
[bold blue]🎯 Enhanced Object Detection System v3.0[/bold blue]

[bold]Configuration:[/bold]
• Model: {self.config.model.path}
• Camera: {self.config.camera.width}x{self.config.camera.height} @ {self.config.camera.fps}fps
• Device: {self.config.model.device}
• Recording: {'Enabled' if self.config.recording.enabled else 'Disabled'}

[bold]Controls:[/bold]
• '{self.config.controls.exit_keys[0].upper()}' or 'ESC' - Exit
• 'SPACE' - Pause/Resume
• '{self.config.controls.reset_key.upper()}' - Reset Statistics
• '{self.config.controls.performance_toggle_key.upper()}' - Toggle Performance
• '{self.config.controls.screenshot_key.upper()}' - Screenshot
• '{self.config.controls.record_toggle_key.upper()}' - Toggle Recording

[green]🚀 Starting detection...[/green]
""",
            title="Startup",
            border_style="blue"
        )
        
        console.print(startup_panel)
    
    def run(self) -> None:
        """Run the main application loop."""
        try:
            self.setup_signal_handlers()
            
            # Initialize components
            if not self.initialize_components():
                rprint("[red]❌ Failed to initialize components[/red]")
                return
            
            # Start camera capture
            if not self.start_camera_capture():
                rprint("[red]❌ Failed to start camera capture[/red]")
                return
            
            # Print startup info
            self.print_startup_info()
            
            # Set running state
            self.state_manager.set_state(AppState.RUNNING)
            
            # Setup display window
            cv2.namedWindow(self.config.display.window_name, cv2.WINDOW_NORMAL)
            if self.fullscreen:
                cv2.setWindowProperty(
                    self.config.display.window_name, 
                    cv2.WND_PROP_FULLSCREEN, 
                    cv2.WINDOW_FULLSCREEN
                )
                rprint("[green]🖥️ Started in fullscreen mode[/green] (Press F to toggle)")
            else:
                cv2.resizeWindow(self.config.display.window_name, 1024, 768)
            
            # Main processing loop
            with Live(self.create_status_table(), refresh_per_second=2) as live:
                self.live_display = live
                
                while not self.shutdown_event.is_set() and not self.state_manager.is_stopping:
                    try:
                        # Get frame from camera
                        frame_data = self.camera_manager.get_frame(timeout=0.1)
                        if not frame_data:
                            continue
                        
                        frame, frame_time = frame_data
                        
                        # Process frame
                        processed_frame = self.process_frame(frame, frame_time)
                        
                        if processed_frame is not None:
                            # Display frame
                            cv2.imshow(self.config.display.window_name, processed_frame)
                            
                            # Handle keyboard input
                            key = cv2.waitKey(1) & 0xFF
                            if key != 255:  # Key pressed
                                if not self.handle_key_input(key):
                                    break
                        
                        # Update live display
                        live.update(self.create_status_table())
                        
                    except KeyboardInterrupt:
                        logger.info("Keyboard interrupt received")
                        break
                    except Exception as e:
                        logger.error(f"Main loop error: {e}")
                        if self.config.development.debug_mode:
                            raise
                        time.sleep(0.1)  # Brief pause on error
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            self.state_manager.error(str(e))
        finally:
            self.cleanup()
    
    def shutdown(self) -> None:
        """Initiate graceful shutdown."""
        logger.info("Initiating application shutdown...")
        self.shutdown_event.set()
        self.state_manager.set_state(AppState.STOPPING)
    
    def cleanup(self) -> None:
        """Cleanup all resources."""
        logger.info("Cleaning up resources...")
        
        try:
            # Stop recording
            if self.video_writer:
                self._stop_recording()
            
            # Release camera
            if self.camera_manager:
                self.camera_manager.release()
            
            # Shutdown detector
            if self.detector:
                self.detector.shutdown()
            
            # Close windows
            cv2.destroyAllWindows()
            
            # Final statistics
            self._print_final_stats()
            
            self.state_manager.set_state(AppState.STOPPED)
            logger.info("Cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def _print_final_stats(self) -> None:
        """Print final application statistics."""
        try:
            runtime = time.time() - self.app_start_time
            perf = self.state_manager.performance
            
            stats_panel = Panel(
                f"""
[bold]📊 Session Statistics[/bold]

• Runtime: {runtime:.1f} seconds
• Frames Processed: {self.frames_processed:,}
• Total Detections: {perf.total_detections:,}
• Average FPS: {perf.fps:.1f}
• Average Detection Time: {perf.avg_detection_time*1000:.1f}ms

[green]✅ Session completed successfully[/green]
""",
                title="Final Statistics",
                border_style="green"
            )
            
            console.print(stats_panel)
            
        except Exception as e:
            logger.error(f"Error printing final stats: {e}")


def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Enhanced Object Detection System v3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_enhanced.py                    # Use default config
  python main_enhanced.py -c custom.yaml    # Use custom config
  python main_enhanced.py --debug           # Enable debug mode
  python main_enhanced.py --camera 1        # Use camera index 1
        """
    )
    
    parser.add_argument(
        "-c", "--config",
        type=str,
        help="Path to configuration file (default: config.yaml)"
    )
    
    parser.add_argument(
        "--camera",
        type=int,
        help="Camera index to use"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        help="Path to YOLO model file"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--no-recording",
        action="store_true",
        help="Disable recording functionality"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level"
    )
    
    return parser


def main() -> int:
    """Main entry point."""
    try:
        # Parse arguments
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # Create application
        app = EnhancedObjectDetectorApp(args.config)
        
        # Apply command line overrides
        if args.camera is not None:
            app.config.camera.index = args.camera
        
        if args.model:
            app.config.model.path = args.model
        
        if args.debug:
            app.config.development.debug_mode = True
        
        if args.no_recording:
            app.config.recording.enabled = False
        
        # Set log level
        from core.logging import set_log_level
        set_log_level(args.log_level)
        
        # Run application
        app.run()
        
        return 0
        
    except KeyboardInterrupt:
        rprint("\n[yellow]👋 Goodbye![/yellow]")
        return 0
    except Exception as e:
        rprint(f"[red]❌ Fatal error: {e}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 