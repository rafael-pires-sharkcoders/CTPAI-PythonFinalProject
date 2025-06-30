"""
Camera management module with error handling and optimization.
"""

import cv2
import threading
import time
from typing import Optional, Tuple, List
from queue import Queue, Empty

from .config import Config, get_config
from .logging import get_logger

logger = get_logger(__name__)


class CameraError(Exception):
    """Custom exception for camera-related errors."""
    pass


class CameraManager:
    """
    Manages camera capture with error handling, buffering, and threading.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize camera manager."""
        self.config = config or get_config()
        self.camera_config = self.config.camera
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.capture_thread: Optional[threading.Thread] = None
        self.frame_queue: Queue = Queue(maxsize=self.camera_config.buffer_size)
        self.lock = threading.Lock()
        
        # Camera statistics
        self.total_frames = 0
        self.dropped_frames = 0
        self.last_frame_time = 0
        
        logger.info("Camera manager initialized")
    
    def find_available_cameras(self) -> List[int]:
        """Find all available camera indices."""
        available_cameras = []
        
        # Test camera indices 0-5
        for idx in range(6):
            try:
                cap = cv2.VideoCapture(idx)
                if cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        available_cameras.append(idx)
                        logger.debug(f"Camera {idx} is available")
                cap.release()
            except Exception as e:
                logger.debug(f"Error testing camera {idx}: {e}")
        
        logger.info(f"Found {len(available_cameras)} available cameras: {available_cameras}")
        return available_cameras
    
    def initialize_camera(self) -> bool:
        """Initialize camera with configuration."""
        try:
            # Find available cameras if the configured one fails
            camera_indices = [self.camera_config.index]
            camera_indices.extend(self.find_available_cameras())
            
            for idx in camera_indices:
                try:
                    logger.info(f"Attempting to initialize camera {idx}")
                    
                    self.cap = cv2.VideoCapture(idx)
                    if not self.cap.isOpened():
                        logger.warning(f"Failed to open camera {idx}")
                        continue
                    
                    # Set camera properties
                    self._configure_camera()
                    
                    # Test capture
                    ret, test_frame = self.cap.read()
                    if not ret or test_frame is None:
                        logger.warning(f"Camera {idx} cannot capture frames")
                        self.cap.release()
                        continue
                    
                    # Log camera information
                    self._log_camera_info(idx, test_frame)
                    
                    logger.info(f"Camera {idx} initialized successfully")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error initializing camera {idx}: {e}")
                    if self.cap:
                        self.cap.release()
                        self.cap = None
                    continue
            
            raise CameraError("No available cameras found")
            
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            return False
    
    def _configure_camera(self) -> None:
        """Configure camera properties."""
        if not self.cap:
            return
        
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_config.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_config.height)
        
        # Set FPS
        self.cap.set(cv2.CAP_PROP_FPS, self.camera_config.fps)
        
        # Set buffer size to reduce latency
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.camera_config.buffer_size)
        
        # Try to enable auto exposure and focus (if supported)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        
        logger.debug("Camera properties configured")
    
    def _log_camera_info(self, idx: int, test_frame) -> None:
        """Log camera information."""
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        
        logger.info(f"Camera {idx} properties:")
        logger.info(f"  Resolution: {actual_width}x{actual_height}")
        logger.info(f"  FPS: {actual_fps}")
        logger.info(f"  Frame shape: {test_frame.shape}")
    
    def start_capture(self) -> bool:
        """Start threaded frame capture."""
        if not self.cap or not self.cap.isOpened():
            logger.error("Camera not initialized")
            return False
        
        if self.is_running:
            logger.warning("Capture already running")
            return True
        
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        logger.info("Frame capture started")
        return True
    
    def _capture_loop(self) -> None:
        """Threaded frame capture loop."""
        logger.debug("Capture loop started")
        
        while self.is_running and self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                current_time = time.time()
                
                if not ret or frame is None:
                    logger.warning("Failed to capture frame")
                    self.dropped_frames += 1
                    time.sleep(0.01)  # Small delay before retry
                    continue
                
                self.total_frames += 1
                self.last_frame_time = current_time
                
                # Add frame to queue (non-blocking)
                try:
                    # Remove old frame if queue is full
                    if self.frame_queue.full():
                        try:
                            self.frame_queue.get_nowait()
                            self.dropped_frames += 1
                        except Empty:
                            pass
                    
                    self.frame_queue.put_nowait((frame, current_time))
                    
                except Exception as e:
                    logger.debug(f"Error adding frame to queue: {e}")
                    self.dropped_frames += 1
                
            except Exception as e:
                logger.error(f"Error in capture loop: {e}")
                time.sleep(0.1)
        
        logger.debug("Capture loop ended")
    
    def get_frame(self, timeout: float = 0.1) -> Optional[Tuple[any, float]]:
        """
        Get the latest frame from the queue.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (frame, timestamp) or None if no frame available
        """
        try:
            return self.frame_queue.get(timeout=timeout)
        except Empty:
            return None
    
    def get_statistics(self) -> dict:
        """Get camera statistics."""
        drop_rate = 0
        if self.total_frames > 0:
            drop_rate = (self.dropped_frames / self.total_frames) * 100
        
        return {
            'total_frames': self.total_frames,
            'dropped_frames': self.dropped_frames,
            'drop_rate_percent': drop_rate,
            'queue_size': self.frame_queue.qsize(),
            'is_running': self.is_running,
            'last_frame_time': self.last_frame_time
        }
    
    def reset_statistics(self) -> None:
        """Reset camera statistics."""
        with self.lock:
            self.total_frames = 0
            self.dropped_frames = 0
            self.last_frame_time = 0
        
        logger.info("Camera statistics reset")
    
    def stop_capture(self) -> None:
        """Stop frame capture."""
        if not self.is_running:
            return
        
        logger.info("Stopping frame capture")
        self.is_running = False
        
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)
            if self.capture_thread.is_alive():
                logger.warning("Capture thread did not stop gracefully")
        
        # Clear frame queue
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except Empty:
                break
        
        logger.info("Frame capture stopped")
    
    def release(self) -> None:
        """Release camera resources."""
        logger.info("Releasing camera resources")
        
        self.stop_capture()
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        logger.info("Camera resources released")
    
    def is_camera_available(self) -> bool:
        """Check if camera is available and working."""
        return (self.cap is not None and 
                self.cap.isOpened() and 
                self.is_running)
    
    def __enter__(self):
        """Context manager entry."""
        if not self.initialize_camera():
            raise CameraError("Failed to initialize camera")
        self.start_capture()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release() 