"""
Application state management module.
"""

import threading
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from .logging import get_logger

logger = get_logger(__name__)


class AppState(Enum):
    """Application states."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class PerformanceMetrics:
    """Performance metrics container."""
    fps: float = 0.0
    avg_detection_time: float = 0.0
    total_detections: int = 0
    frame_count: int = 0
    dropped_frames: int = 0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    
    # Moving averages
    fps_history: List[float] = field(default_factory=list)
    detection_time_history: List[float] = field(default_factory=list)
    
    def update_fps(self, fps: float, window_size: int = 30) -> None:
        """Update FPS with moving average."""
        self.fps_history.append(fps)
        if len(self.fps_history) > window_size:
            self.fps_history.pop(0)
        self.fps = sum(self.fps_history) / len(self.fps_history)
    
    def update_detection_time(self, detection_time: float, window_size: int = 100) -> None:
        """Update detection time with moving average."""
        self.detection_time_history.append(detection_time)
        if len(self.detection_time_history) > window_size:
            self.detection_time_history.pop(0)
        self.avg_detection_time = sum(self.detection_time_history) / len(self.detection_time_history)
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.fps = 0.0
        self.avg_detection_time = 0.0
        self.total_detections = 0
        self.frame_count = 0
        self.dropped_frames = 0
        self.memory_usage = 0.0
        self.cpu_usage = 0.0
        self.fps_history.clear()
        self.detection_time_history.clear()


class StateManager:
    """
    Manages application state and performance metrics.
    Thread-safe state management with event notifications.
    """
    
    def __init__(self):
        """Initialize state manager."""
        self._state = AppState.INITIALIZING
        self._performance = PerformanceMetrics()
        self._lock = threading.RLock()
        self._state_listeners = []
        
        # Application flags
        self._show_performance = False
        self._recording = False
        self._debug_mode = False
        
        # Timing
        self._last_fps_calculation = time.time()
        self._frame_times = []
        
        logger.info("State manager initialized")
    
    def add_state_listener(self, callback) -> None:
        """Add a state change listener."""
        with self._lock:
            self._state_listeners.append(callback)
    
    def remove_state_listener(self, callback) -> None:
        """Remove a state change listener."""
        with self._lock:
            if callback in self._state_listeners:
                self._state_listeners.remove(callback)
    
    def _notify_state_change(self, old_state: AppState, new_state: AppState) -> None:
        """Notify listeners of state change."""
        for callback in self._state_listeners:
            try:
                callback(old_state, new_state)
            except Exception as e:
                logger.error(f"Error in state listener: {e}")
    
    @property
    def state(self) -> AppState:
        """Get current application state."""
        with self._lock:
            return self._state
    
    def set_state(self, new_state: AppState) -> None:
        """Set application state."""
        with self._lock:
            old_state = self._state
            if old_state != new_state:
                self._state = new_state
                logger.info(f"State changed: {old_state.value} -> {new_state.value}")
                self._notify_state_change(old_state, new_state)
    
    @property
    def is_running(self) -> bool:
        """Check if application is running."""
        return self.state == AppState.RUNNING
    
    @property
    def is_paused(self) -> bool:
        """Check if application is paused."""
        return self.state == AppState.PAUSED
    
    @property
    def is_stopping(self) -> bool:
        """Check if application is stopping."""
        return self.state in [AppState.STOPPING, AppState.STOPPED]
    
    def pause(self) -> None:
        """Pause application."""
        if self.state == AppState.RUNNING:
            self.set_state(AppState.PAUSED)
    
    def resume(self) -> None:
        """Resume application."""
        if self.state == AppState.PAUSED:
            self.set_state(AppState.RUNNING)
    
    def toggle_pause(self) -> None:
        """Toggle pause state."""
        if self.is_paused:
            self.resume()
        elif self.is_running:
            self.pause()
    
    def stop(self) -> None:
        """Stop application."""
        self.set_state(AppState.STOPPING)
    
    def error(self, error_message: str) -> None:
        """Set error state."""
        logger.error(f"Application error: {error_message}")
        self.set_state(AppState.ERROR)
    
    # Performance metrics management
    @property
    def performance(self) -> PerformanceMetrics:
        """Get performance metrics (read-only copy)."""
        with self._lock:
            return PerformanceMetrics(
                fps=self._performance.fps,
                avg_detection_time=self._performance.avg_detection_time,
                total_detections=self._performance.total_detections,
                frame_count=self._performance.frame_count,
                dropped_frames=self._performance.dropped_frames,
                memory_usage=self._performance.memory_usage,
                cpu_usage=self._performance.cpu_usage
            )
    
    def update_frame_count(self) -> None:
        """Update frame count and calculate FPS."""
        with self._lock:
            current_time = time.time()
            self._frame_times.append(current_time)
            self._performance.frame_count += 1
            
            # Calculate FPS every second
            if current_time - self._last_fps_calculation >= 1.0:
                # Remove frames older than 1 second
                cutoff_time = current_time - 1.0
                self._frame_times = [t for t in self._frame_times if t > cutoff_time]
                
                # Calculate FPS
                fps = len(self._frame_times)
                self._performance.update_fps(fps)
                self._last_fps_calculation = current_time
    
    def update_detection_time(self, detection_time: float) -> None:
        """Update detection time metrics."""
        with self._lock:
            self._performance.update_detection_time(detection_time)
    
    def increment_detections(self, count: int = 1) -> None:
        """Increment detection count."""
        with self._lock:
            self._performance.total_detections += count
    
    def increment_dropped_frames(self, count: int = 1) -> None:
        """Increment dropped frame count."""
        with self._lock:
            self._performance.dropped_frames += count
    
    def update_system_metrics(self, memory_usage: float, cpu_usage: float) -> None:
        """Update system resource metrics."""
        with self._lock:
            self._performance.memory_usage = memory_usage
            self._performance.cpu_usage = cpu_usage
    
    def reset_performance(self) -> None:
        """Reset performance metrics."""
        with self._lock:
            self._performance.reset()
            self._frame_times.clear()
            self._last_fps_calculation = time.time()
        logger.info("Performance metrics reset")
    
    # Application flags
    @property
    def show_performance(self) -> bool:
        """Check if performance info should be shown."""
        with self._lock:
            return self._show_performance
    
    def toggle_performance_display(self) -> None:
        """Toggle performance display."""
        with self._lock:
            self._show_performance = not self._show_performance
            logger.info(f"Performance display: {'enabled' if self._show_performance else 'disabled'}")
    
    @property
    def is_recording(self) -> bool:
        """Check if recording is active."""
        with self._lock:
            return self._recording
    
    def start_recording(self) -> None:
        """Start recording."""
        with self._lock:
            self._recording = True
            logger.info("Recording started")
    
    def stop_recording(self) -> None:
        """Stop recording."""
        with self._lock:
            self._recording = False
            logger.info("Recording stopped")
    
    def toggle_recording(self) -> None:
        """Toggle recording state."""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    @property
    def debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        with self._lock:
            return self._debug_mode
    
    def set_debug_mode(self, enabled: bool) -> None:
        """Set debug mode."""
        with self._lock:
            self._debug_mode = enabled
            logger.info(f"Debug mode: {'enabled' if enabled else 'disabled'}")
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get complete state summary."""
        with self._lock:
            perf = self.performance
            return {
                'state': self.state.value,
                'show_performance': self.show_performance,
                'recording': self.is_recording,
                'debug_mode': self.debug_mode,
                'performance': {
                    'fps': perf.fps,
                    'avg_detection_time_ms': perf.avg_detection_time * 1000,
                    'total_detections': perf.total_detections,
                    'frame_count': perf.frame_count,
                    'dropped_frames': perf.dropped_frames,
                    'memory_usage_mb': perf.memory_usage,
                    'cpu_usage_percent': perf.cpu_usage
                }
            } 