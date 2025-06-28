"""
Enhanced YOLO detector with improved error handling, type safety, and performance.
"""

import cv2
import numpy as np
import time
import threading
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from ultralytics import YOLO
import psutil

from core.config import Config, get_config
from core.logging import get_logger

logger = get_logger(__name__)

# Type aliases for better readability
Detection = Tuple[float, float, float, float, str, float]  # x1, y1, x2, y2, label, confidence
BoundingBox = Tuple[float, float, float, float]  # x1, y1, x2, y2


class DetectorError(Exception):
    """Custom exception for detector-related errors."""
    pass


class ModelLoadError(DetectorError):
    """Exception raised when model fails to load."""
    pass


class InferenceError(DetectorError):
    """Exception raised during inference."""
    pass


class EnhancedYOLODetector:
    """
    Enhanced YOLO detector with improved performance, error handling, and monitoring.
    
    Features:
    - Thread-safe operations
    - Comprehensive error handling
    - Performance monitoring
    - Configurable inference parameters
    - Resource usage tracking
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the enhanced YOLO detector.
        
        Args:
            config: Configuration object, uses global config if None
            
        Raises:
            ModelLoadError: If model fails to load
        """
        self.config = config or get_config()
        self.model_config = self.config.model
        
        # Initialize model
        self.model: Optional[YOLO] = None
        self.model_info: Dict[str, Any] = {}
        
        # Performance tracking
        self.inference_times: List[float] = []
        self.total_inferences = 0
        self.successful_inferences = 0
        self.failed_inferences = 0
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Class colors cache
        self.class_colors: Dict[str, Tuple[int, int, int]] = {}
        self.color_index = 0
        
        # Thread pool for async operations
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.config.performance.thread_pool_size
        )
        
        logger.info("Enhanced YOLO detector initializing...")
        self._load_model()
        logger.info("Enhanced YOLO detector initialized successfully")
    
    def _load_model(self) -> None:
        """
        Load YOLO model with error handling and validation.
        
        Raises:
            ModelLoadError: If model fails to load or validate
        """
        try:
            model_path = Path(self.model_config.path)
            
            if not model_path.exists():
                raise ModelLoadError(f"Model file not found: {model_path}")
            
            logger.info(f"Loading YOLO model: {model_path}")
            
            # Load model
            self.model = YOLO(str(model_path))
            
            # Validate model
            self._validate_model()
            
            # Warm up model with dummy inference
            self._warmup_model()
            
            # Store model information
            self._store_model_info()
            
            logger.info(f"Model loaded successfully: {self.model_info['num_classes']} classes")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise ModelLoadError(f"Model loading failed: {e}") from e
    
    def _validate_model(self) -> None:
        """Validate that the model is properly loaded."""
        if not self.model:
            raise ModelLoadError("Model is None after loading")
        
        if not hasattr(self.model, 'names') or not self.model.names:
            raise ModelLoadError("Model does not have class names")
        
        logger.debug(f"Model validation passed: {len(self.model.names)} classes found")
    
    def _warmup_model(self) -> None:
        """Warm up model with dummy inference to reduce first-inference latency."""
        try:
            dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            logger.debug("Warming up model...")
            start_time = time.time()
            
            # Perform dummy inference
            _ = self.model(
                dummy_frame,
                conf=self.model_config.confidence_threshold,
                iou=self.model_config.iou_threshold,
                verbose=False,
                device=self.model_config.device,
                half=self.model_config.half_precision
            )
            
            warmup_time = time.time() - start_time
            logger.debug(f"Model warmup completed in {warmup_time:.3f}s")
            
        except Exception as e:
            logger.warning(f"Model warmup failed: {e}")
    
    def _store_model_info(self) -> None:
        """Store model information for reference."""
        if not self.model:
            return
        
        self.model_info = {
            'path': self.model_config.path,
            'classes': list(self.model.names.values()),
            'num_classes': len(self.model.names),
            'class_names': dict(self.model.names),
            'confidence_threshold': self.model_config.confidence_threshold,
            'iou_threshold': self.model_config.iou_threshold,
            'device': self.model_config.device,
            'half_precision': self.model_config.half_precision
        }
    
    def get_class_color(self, label: str) -> Tuple[int, int, int]:
        """
        Get consistent color for a class label.
        
        Args:
            label: Class label
            
        Returns:
            BGR color tuple
        """
        with self.lock:
            if label not in self.class_colors:
                colors = self.config.display.class_colors
                color = colors[self.color_index % len(colors)]
                self.class_colors[label] = tuple(color)
                self.color_index += 1
            
            return self.class_colors[label]
    
    def detect_objects(self, frame: np.ndarray) -> List[Detection]:
        """
        Detect objects in a frame with comprehensive error handling.
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            List of detections as (x1, y1, x2, y2, label, confidence) tuples
            
        Raises:
            InferenceError: If inference fails
        """
        if not self._is_valid_frame(frame):
            raise InferenceError("Invalid input frame")
        
        if not self.model:
            raise InferenceError("Model not loaded")
        
        start_time = time.time()
        
        try:
            with self.lock:
                self.total_inferences += 1
            
            # Perform inference
            results = self.model(
                frame,
                conf=self.model_config.confidence_threshold,
                iou=self.model_config.iou_threshold,
                verbose=False,
                device=self.model_config.device,
                half=self.model_config.half_precision
            )
            
            # Process results
            detections = self._process_results(results)
            
            # Update statistics
            inference_time = time.time() - start_time
            self._update_inference_stats(inference_time, success=True)
            
            logger.debug(f"Detection completed: {len(detections)} objects in {inference_time:.3f}s")
            
            return detections
            
        except Exception as e:
            self._update_inference_stats(time.time() - start_time, success=False)
            logger.error(f"Inference failed: {e}")
            raise InferenceError(f"Object detection failed: {e}") from e
    
    def _is_valid_frame(self, frame: np.ndarray) -> bool:
        """Validate input frame."""
        if frame is None:
            return False
        
        if not isinstance(frame, np.ndarray):
            return False
        
        if frame.size == 0:
            return False
        
        if len(frame.shape) != 3 or frame.shape[2] != 3:
            return False
        
        return True
    
    def _process_results(self, results) -> List[Detection]:
        """
        Process YOLO results into standardized detection format.
        
        Args:
            results: YOLO inference results
            
        Returns:
            List of processed detections
        """
        detections = []
        
        try:
            for result in results:
                if result.boxes is None or len(result.boxes) == 0:
                    continue
                
                # Limit number of detections
                boxes = result.boxes[:self.model_config.max_detections]
                
                for box in boxes:
                    try:
                        detection = self._process_single_box(box)
                        if detection:
                            detections.append(detection)
                    except Exception as e:
                        logger.debug(f"Failed to process box: {e}")
                        continue
            
        except Exception as e:
            logger.error(f"Failed to process results: {e}")
        
        return detections
    
    def _process_single_box(self, box) -> Optional[Detection]:
        """
        Process a single detection box.
        
        Args:
            box: YOLO detection box
            
        Returns:
            Detection tuple or None if invalid
        """
        try:
            # Extract coordinates
            xyxy = box.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])
            
            # Validate coordinates
            if x1 >= x2 or y1 >= y2:
                return None
            
            # Extract class and confidence
            class_id = int(box.cls[0].cpu().numpy())
            confidence = float(box.conf[0].cpu().numpy())
            
            # Validate class ID
            if class_id not in self.model.names:
                return None
            
            label = self.model.names[class_id]
            
            return (x1, y1, x2, y2, label, confidence)
            
        except Exception as e:
            logger.debug(f"Error processing box: {e}")
            return None
    
    def _update_inference_stats(self, inference_time: float, success: bool) -> None:
        """Update inference statistics."""
        with self.lock:
            self.inference_times.append(inference_time)
            
            # Keep only recent measurements
            if len(self.inference_times) > self.config.performance.fps_calculation_window:
                self.inference_times.pop(0)
            
            if success:
                self.successful_inferences += 1
            else:
                self.failed_inferences += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive performance statistics.
        
        Returns:
            Dictionary containing performance metrics
        """
        with self.lock:
            if not self.inference_times:
                return {
                    'avg_inference_time': 0.0,
                    'fps_estimate': 0.0,
                    'total_inferences': self.total_inferences,
                    'successful_inferences': self.successful_inferences,
                    'failed_inferences': self.failed_inferences,
                    'success_rate': 0.0
                }
            
            avg_time = sum(self.inference_times) / len(self.inference_times)
            fps_estimate = 1.0 / avg_time if avg_time > 0 else 0.0
            success_rate = (self.successful_inferences / self.total_inferences * 100 
                          if self.total_inferences > 0 else 0.0)
            
            return {
                'avg_inference_time': avg_time,
                'fps_estimate': fps_estimate,
                'total_inferences': self.total_inferences,
                'successful_inferences': self.successful_inferences,
                'failed_inferences': self.failed_inferences,
                'success_rate': success_rate,
                'recent_inference_count': len(self.inference_times)
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return self.model_info.copy()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system resource information."""
        try:
            process = psutil.Process()
            return {
                'memory_usage_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent(),
                'thread_count': process.num_threads(),
                'system_memory_percent': psutil.virtual_memory().percent,
                'system_cpu_percent': psutil.cpu_percent()
            }
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {}
    
    def reset_stats(self) -> None:
        """Reset all performance statistics."""
        with self.lock:
            self.inference_times.clear()
            self.total_inferences = 0
            self.successful_inferences = 0
            self.failed_inferences = 0
        
        logger.info("Detector statistics reset")
    
    def shutdown(self) -> None:
        """Cleanup resources."""
        logger.info("Shutting down detector...")
        
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)
        
        self.model = None
        logger.info("Detector shutdown complete")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown() 