"""
Enhanced display and user interface module with improved drawing functions.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any

from core.config import Config, get_config
from core.logging import get_logger

logger = get_logger(__name__)

# Type aliases
Color = Tuple[int, int, int]
Detection = Tuple[float, float, float, float, str, float]


class InterfaceDrawer:
    """
    Enhanced interface drawer with configurable styling and error handling.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the interface drawer."""
        self.config = config or get_config()
        self.display_config = self.config.display
        
        # Font settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = self.display_config.font_scale
        self.font_thickness = self.display_config.font_thickness
        self.box_thickness = self.display_config.box_thickness
        
        # Colors
        self.colors = self.display_config.colors
        self.class_colors = self.display_config.class_colors
        
        # Class color cache
        self.class_color_cache: Dict[str, Color] = {}
        self.color_index = 0
        
        logger.debug("Interface drawer initialized")
    
    def get_class_color(self, class_name: str) -> Color:
        """Get consistent color for a class."""
        if class_name not in self.class_color_cache:
            color = self.class_colors[self.color_index % len(self.class_colors)]
            self.class_color_cache[class_name] = tuple(color)
            self.color_index += 1
        
        return self.class_color_cache[class_name]
    
    def draw_bounding_box(
        self, 
        frame: np.ndarray, 
        x1: float, 
        y1: float, 
        x2: float, 
        y2: float, 
        label: str, 
        confidence: float,
        color: Optional[Color] = None
    ) -> bool:
        """
        Draw bounding box with label and confidence.
        
        Args:
            frame: Target frame
            x1, y1, x2, y2: Bounding box coordinates
            label: Object label
            confidence: Detection confidence
            color: Box color (optional)
            
        Returns:
            True if drawn successfully, False otherwise
        """
        try:
            if color is None:
                color = self.get_class_color(label)
            
            # Convert to integers and validate
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Ensure coordinates are within frame bounds
            height, width = frame.shape[:2]
            x1 = max(0, min(x1, width - 1))
            y1 = max(0, min(y1, height - 1))
            x2 = max(0, min(x2, width - 1))
            y2 = max(0, min(y2, height - 1))
            
            # Validate box dimensions
            if x1 >= x2 or y1 >= y2:
                return False
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, self.box_thickness)
            
            # Prepare label text
            if self.display_config.show_confidence:
                text = f"{label}: {confidence:.2f}"
            else:
                text = label
            
            # Calculate text size and position
            (text_width, text_height), baseline = cv2.getTextSize(
                text, self.font, self.font_scale, self.font_thickness
            )
            
            # Position text above box, or below if not enough space
            text_y = y1 - 10
            if text_y - text_height < 0:
                text_y = y2 + text_height + 10
            
            # Ensure text stays within frame
            text_x = max(0, min(x1, width - text_width))
            text_y = max(text_height, min(text_y, height - 5))
            
            # Draw text background
            bg_x1 = max(0, text_x - 2)
            bg_y1 = max(0, text_y - text_height - 2)
            bg_x2 = min(width, text_x + text_width + 2)
            bg_y2 = min(height, text_y + 2)
            
            if bg_x1 < bg_x2 and bg_y1 < bg_y2:
                cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), color, -1)
            
            # Draw text
            cv2.putText(
                frame, text, (text_x, text_y),
                self.font, self.font_scale, self.colors.text,
                self.font_thickness, cv2.LINE_AA
            )
            
            return True
            
        except Exception as e:
            logger.debug(f"Error drawing bounding box: {e}")
            return False
    
    def draw_detections(self, frame: np.ndarray, detections: List[Detection]) -> int:
        """
        Draw all detections on frame.
        
        Args:
            frame: Target frame
            detections: List of detections
            
        Returns:
            Number of successfully drawn detections
        """
        drawn_count = 0
        
        for detection in detections:
            try:
                x1, y1, x2, y2, label, confidence = detection
                if self.draw_bounding_box(frame, x1, y1, x2, y2, label, confidence):
                    drawn_count += 1
            except Exception as e:
                logger.debug(f"Error drawing detection: {e}")
        
        return drawn_count
    
    def draw_fps(self, frame: np.ndarray, fps: float) -> None:
        """Draw FPS counter."""
        try:
            fps_text = f"FPS: {fps:.1f}"
            self._draw_info_box(
                frame, fps_text, 
                position="top_right", 
                color=self.colors.fps
            )
        except Exception as e:
            logger.debug(f"Error drawing FPS: {e}")
    
    def draw_detection_count(self, frame: np.ndarray, count: int) -> None:
        """Draw detection count."""
        try:
            count_text = f"Objects: {count}"
            self._draw_info_box(
                frame, count_text,
                position="top_left",
                color=self.colors.counter
            )
        except Exception as e:
            logger.debug(f"Error drawing detection count: {e}")
    
    def draw_performance_info(self, frame: np.ndarray, stats: Dict[str, Any]) -> None:
        """Draw performance information."""
        try:
            if not stats:
                return
            
            # Prepare performance text
            lines = []
            
            if 'avg_inference_time' in stats:
                avg_time_ms = stats['avg_inference_time'] * 1000
                lines.append(f"Inference: {avg_time_ms:.1f}ms")
            
            if 'total_inferences' in stats:
                lines.append(f"Total: {stats['total_inferences']}")
            
            if 'success_rate' in stats:
                lines.append(f"Success: {stats['success_rate']:.1f}%")
            
            if 'memory_usage_mb' in stats:
                lines.append(f"Memory: {stats['memory_usage_mb']:.1f}MB")
            
            # Draw performance info box
            self._draw_multi_line_info_box(
                frame, lines,
                position="bottom_left",
                color=self.colors.background
            )
            
        except Exception as e:
            logger.debug(f"Error drawing performance info: {e}")
    
    def draw_status_message(
        self, 
        frame: np.ndarray, 
        message: str, 
        color: Optional[Color] = None
    ) -> None:
        """Draw centered status message."""
        try:
            if color is None:
                color = self.colors.primary
            
            # Calculate center position
            height, width = frame.shape[:2]
            (text_width, text_height), _ = cv2.getTextSize(
                message, self.font, 0.8, 2
            )
            
            x = (width - text_width) // 2
            y = (height + text_height) // 2
            
            # Draw background
            padding = 10
            cv2.rectangle(
                frame,
                (x - padding, y - text_height - padding),
                (x + text_width + padding, y + padding),
                self.colors.background,
                -1
            )
            
            # Draw text
            cv2.putText(
                frame, message, (x, y),
                self.font, 0.8, color, 2, cv2.LINE_AA
            )
            
        except Exception as e:
            logger.debug(f"Error drawing status message: {e}")
    
    def draw_recording_indicator(self, frame: np.ndarray) -> None:
        """Draw recording indicator."""
        try:
            height, width = frame.shape[:2]
            
            # Draw red circle in top-right corner
            center = (width - 30, 30)
            cv2.circle(frame, center, 8, (0, 0, 255), -1)
            
            # Draw "REC" text
            cv2.putText(
                frame, "REC", (width - 60, 35),
                self.font, 0.4, (0, 0, 255), 1, cv2.LINE_AA
            )
            
        except Exception as e:
            logger.debug(f"Error drawing recording indicator: {e}")
    
    def _draw_info_box(
        self, 
        frame: np.ndarray, 
        text: str, 
        position: str = "top_left",
        color: Color = (255, 255, 255)
    ) -> None:
        """Draw information box with background."""
        try:
            height, width = frame.shape[:2]
            
            # Calculate text size
            (text_width, text_height), baseline = cv2.getTextSize(
                text, self.font, 0.6, 2
            )
            
            # Calculate position
            padding = 5
            if position == "top_left":
                x, y = padding, text_height + padding
            elif position == "top_right":
                x, y = width - text_width - padding, text_height + padding
            elif position == "bottom_left":
                x, y = padding, height - padding
            else:  # bottom_right
                x, y = width - text_width - padding, height - padding
            
            # Draw background
            cv2.rectangle(
                frame,
                (x - padding, y - text_height - padding),
                (x + text_width + padding, y + padding),
                self.colors.background,
                -1
            )
            
            # Draw text
            cv2.putText(
                frame, text, (x, y),
                self.font, 0.6, color, 2, cv2.LINE_AA
            )
            
        except Exception as e:
            logger.debug(f"Error drawing info box: {e}")
    
    def _draw_multi_line_info_box(
        self, 
        frame: np.ndarray, 
        lines: List[str], 
        position: str = "bottom_left",
        color: Color = (200, 200, 200)
    ) -> None:
        """Draw multi-line information box."""
        try:
            if not lines:
                return
            
            height, width = frame.shape[:2]
            line_height = 20
            padding = 5
            
            # Calculate total text dimensions
            max_width = 0
            for line in lines:
                (text_width, _), _ = cv2.getTextSize(line, self.font, 0.4, 1)
                max_width = max(max_width, text_width)
            
            total_height = len(lines) * line_height
            
            # Calculate position
            if position == "bottom_left":
                x = padding
                y = height - total_height - padding
            else:  # Add more positions as needed
                x = padding
                y = height - total_height - padding
            
            # Draw background
            cv2.rectangle(
                frame,
                (x - padding, y - padding),
                (x + max_width + padding, y + total_height + padding),
                self.colors.background,
                -1
            )
            
            # Draw lines
            for i, line in enumerate(lines):
                line_y = y + (i + 1) * line_height - 5
                cv2.putText(
                    frame, line, (x, line_y),
                    self.font, 0.4, color, 1, cv2.LINE_AA
                )
                
        except Exception as e:
            logger.debug(f"Error drawing multi-line info box: {e}")
    
    def draw_debug_info(self, frame: np.ndarray, debug_data: Dict[str, Any]) -> None:
        """Draw debug information."""
        try:
            debug_lines = []
            
            for key, value in debug_data.items():
                if isinstance(value, float):
                    debug_lines.append(f"{key}: {value:.3f}")
                else:
                    debug_lines.append(f"{key}: {value}")
            
            if debug_lines:
                self._draw_multi_line_info_box(
                    frame, debug_lines,
                    position="bottom_right",
                    color=(128, 128, 128)
                )
                
        except Exception as e:
            logger.debug(f"Error drawing debug info: {e}") 