"""
Configuration management using Pydantic for type safety and validation.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union

import yaml
from pydantic import BaseModel, Field, validator
from rich.console import Console

console = Console()


class CameraConfig(BaseModel):
    """Camera configuration settings."""
    
    index: int = Field(default=0, ge=0, description="Camera index")
    width: int = Field(default=640, gt=0, description="Frame width")
    height: int = Field(default=480, gt=0, description="Frame height")
    fps: int = Field(default=30, gt=0, le=120, description="Target FPS")
    buffer_size: int = Field(default=1, ge=1, le=10, description="Camera buffer size")


class ModelConfig(BaseModel):
    """YOLO model configuration settings."""
    
    path: str = Field(default="yolov8n.pt", description="Model file path")
    confidence_threshold: float = Field(default=0.4, ge=0.0, le=1.0, description="Confidence threshold")
    iou_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="IoU threshold for NMS")
    device: str = Field(default="cpu", description="Inference device")
    half_precision: bool = Field(default=False, description="Use half precision")
    max_detections: int = Field(default=50, gt=0, le=1000, description="Maximum detections per frame")

    @validator('device')
    def validate_device(cls, v: str) -> str:
        """Validate device setting."""
        allowed_devices = ["cpu", "cuda", "mps"]
        if v not in allowed_devices:
            raise ValueError(f"Device must be one of {allowed_devices}")
        return v


class PerformanceConfig(BaseModel):
    """Performance optimization settings."""
    
    skip_frames: int = Field(default=0, ge=0, le=10, description="Skip N frames between processing")
    fps_calculation_window: int = Field(default=100, gt=0, description="FPS calculation window")
    enable_threading: bool = Field(default=True, description="Enable multithreading")
    thread_pool_size: int = Field(default=2, ge=1, le=8, description="Thread pool size")


class StabilityConfig(BaseModel):
    """Detection stability and anti-flickering settings."""
    
    enable_tracking: bool = Field(default=True, description="Enable detection tracking")
    detection_buffer_size: int = Field(default=3, ge=1, le=10, description="Buffer size for detection stability")
    confidence_smoothing: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence smoothing factor")
    position_tolerance: int = Field(default=30, ge=5, le=100, description="Position tolerance in pixels")
    min_stable_frames: int = Field(default=2, ge=1, le=10, description="Minimum frames for stable detection")


class DisplayColors(BaseModel):
    """Display color configuration."""
    
    primary: List[int] = Field(default=[0, 255, 0], description="Primary color (BGR)")
    text: List[int] = Field(default=[255, 255, 255], description="Text color (BGR)")
    background: List[int] = Field(default=[0, 0, 0], description="Background color (BGR)")
    fps: List[int] = Field(default=[0, 255, 255], description="FPS display color (BGR)")
    counter: List[int] = Field(default=[255, 255, 0], description="Counter display color (BGR)")
    
    @validator('primary', 'text', 'background', 'fps', 'counter')
    def validate_color(cls, v: List[int]) -> List[int]:
        """Validate color values."""
        if len(v) != 3:
            raise ValueError("Color must have exactly 3 values (BGR)")
        if not all(0 <= val <= 255 for val in v):
            raise ValueError("Color values must be between 0 and 255")
        return v


class DisplayConfig(BaseModel):
    """Display configuration settings."""
    
    window_name: str = Field(default="Object Detector - Enhanced", description="Window title")
    fullscreen: bool = Field(default=False, description="Start in fullscreen mode")
    show_fps: bool = Field(default=True, description="Show FPS counter")
    show_detection_count: bool = Field(default=True, description="Show detection count")
    show_confidence: bool = Field(default=True, description="Show confidence scores")
    box_thickness: int = Field(default=2, ge=1, le=10, description="Bounding box thickness")
    font_scale: float = Field(default=0.5, gt=0.0, le=2.0, description="Font scale")
    font_thickness: int = Field(default=1, ge=1, le=5, description="Font thickness")
    colors: DisplayColors = Field(default_factory=DisplayColors, description="Color configuration")
    class_colors: List[List[int]] = Field(
        default=[
            [255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0], [255, 0, 255],
            [0, 255, 255], [128, 0, 128], [255, 165, 0], [0, 128, 255], [128, 255, 0]
        ],
        description="Colors for object classes"
    )


class ControlsConfig(BaseModel):
    """Input controls configuration."""
    
    exit_keys: List[str] = Field(default=['q', 'esc'], description="Keys to exit application")
    pause_key: str = Field(default='space', description="Key to pause/unpause")
    reset_key: str = Field(default='r', description="Key to reset statistics")
    performance_toggle_key: str = Field(default='p', description="Key to toggle performance info")
    screenshot_key: str = Field(default='s', description="Key to take screenshot")
    record_toggle_key: str = Field(default='v', description="Key to toggle recording")
    fullscreen_toggle_key: str = Field(default='f', description="Key to toggle fullscreen")


class RecordingConfig(BaseModel):
    """Video recording configuration."""
    
    enabled: bool = Field(default=True, description="Enable recording feature")
    output_dir: str = Field(default="recordings", description="Output directory")
    codec: str = Field(default="XVID", description="Video codec")
    extension: str = Field(default=".avi", description="File extension")
    fps: int = Field(default=30, gt=0, le=120, description="Recording FPS")

    @validator('codec')
    def validate_codec(cls, v: str) -> str:
        """Validate video codec."""
        allowed_codecs = ["XVID", "MJPG", "MP4V", "H264"]
        if v not in allowed_codecs:
            raise ValueError(f"Codec must be one of {allowed_codecs}")
        return v


class LoggingConfig(BaseModel):
    """Logging configuration."""
    
    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    file: str = Field(default="logs/detector.log", description="Log file path")
    max_file_size: int = Field(default=10485760, gt=0, description="Max log file size in bytes")
    backup_count: int = Field(default=5, ge=0, description="Number of backup log files")
    console_output: bool = Field(default=True, description="Enable console output")

    @validator('level')
    def validate_level(cls, v: str) -> str:
        """Validate logging level."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"Logging level must be one of {allowed_levels}")
        return v_upper


class DevelopmentConfig(BaseModel):
    """Development and debugging configuration."""
    
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    profiling: bool = Field(default=False, description="Enable performance profiling")
    save_failed_frames: bool = Field(default=False, description="Save frames that failed processing")
    performance_metrics: bool = Field(default=True, description="Collect performance metrics")


class Config(BaseModel):
    """Main configuration class."""
    
    camera: CameraConfig = Field(default_factory=CameraConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    stability: StabilityConfig = Field(default_factory=StabilityConfig)
    display: DisplayConfig = Field(default_factory=DisplayConfig)
    controls: ControlsConfig = Field(default_factory=ControlsConfig)
    recording: RecordingConfig = Field(default_factory=RecordingConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    development: DevelopmentConfig = Field(default_factory=DevelopmentConfig)

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"

    def create_directories(self) -> None:
        """Create necessary directories."""
        # Create logs directory
        log_dir = Path(self.logging.file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create recordings directory
        if self.recording.enabled:
            recording_dir = Path(self.recording.output_dir)
            recording_dir.mkdir(parents=True, exist_ok=True)
        
        # Create failed frames directory if debugging
        if self.development.save_failed_frames:
            failed_frames_dir = Path("debug/failed_frames")
            failed_frames_dir.mkdir(parents=True, exist_ok=True)


class ConfigManager:
    """Configuration manager with YAML support."""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialize configuration manager."""
        self.config_path = Path(config_path) if config_path else Path("config.yaml")
        self._config: Optional[Config] = None
    
    def load_config(self) -> Config:
        """Load configuration from YAML file."""
        try:
            if not self.config_path.exists():
                console.print(f"[yellow]Config file not found at {self.config_path}. Using defaults.[/yellow]")
                self._config = Config()
                self.save_config()
                return self._config
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            self._config = Config(**config_data)
            self._config.create_directories()
            
            console.print(f"[green]Configuration loaded from {self.config_path}[/green]")
            return self._config
            
        except Exception as e:
            console.print(f"[red]Error loading config: {e}[/red]")
            console.print("[yellow]Using default configuration[/yellow]")
            self._config = Config()
            return self._config
    
    def save_config(self) -> None:
        """Save current configuration to YAML file."""
        if not self._config:
            return
        
        try:
            config_dict = self._config.dict()
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            console.print(f"[green]Configuration saved to {self.config_path}[/green]")
            
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")
    
    def get_config(self) -> Config:
        """Get current configuration."""
        if not self._config:
            return self.load_config()
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration values."""
        if not self._config:
            self.load_config()
        
        try:
            for key, value in kwargs.items():
                if hasattr(self._config, key):
                    setattr(self._config, key, value)
            
            self.save_config()
            
        except Exception as e:
            console.print(f"[red]Error updating config: {e}[/red]")


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config_manager.get_config()


def reload_config() -> Config:
    """Reload configuration from file."""
    return config_manager.load_config() 