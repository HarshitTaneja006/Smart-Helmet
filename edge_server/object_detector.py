"""
object_detector.py
YOLOv5 ONNX inference using OpenCV DNN
"""

import cv2
import numpy as np
import logging
from typing import List, Tuple
import config
import os

logger = logging.getLogger(__name__)

class ObjectDetector:
    """
    YOLOv5 ONNX Object Detector using OpenCV DNN
    
    Methods:
        detect(frame) -> List[Detection]
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize YOLO detector
        
        Args:
            model_path: Path to ONNX model file
        """
        self.model_path = model_path or config.YOLO_MODEL_PATH
        self.input_size = config.YOLO_INPUT_SIZE
        self.confidence_threshold = config.DETECTION_CONFIDENCE
        self.nms_threshold = config.NMS_THRESHOLD
        self.classes = config.COCO_CLASSES
        
        logger.info("Initializing YOLOv5 detector...")
        logger.info(f"Model path: {self.model_path}")
        
        # Check if model file exists
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        # Load ONNX model using OpenCV DNN
        try:
            self.net = cv2.dnn.readNetFromONNX(self.model_path)
            logger.info("✓ ONNX model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load ONNX model: {e}")
            raise
        
        # Set backend and target
        # Use CUDA only if OpenCV was built with CUDA support
        cuda_available = cv2.cuda.getCudaEnabledDeviceCount() > 0 if hasattr(cv2, 'cuda') else False
        if cuda_available:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            logger.info("✓ Using CUDA backend")
        else:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            logger.info("✓ Using CPU backend")
        
        logger.info(f"Confidence threshold: {self.confidence_threshold}")
        logger.info(f"NMS threshold: {self.nms_threshold}")
    
    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocess frame for YOLO input
        
        Args:
            frame: Input image (BGR)
        
        Returns:
            Preprocessed blob
        """
        # Create blob: resize, normalize, swap channels
        blob = cv2.dnn.blobFromImage(
            frame,
            scalefactor=1.0 / 255.0,
            size=(self.input_size, self.input_size),
            mean=[0, 0, 0],
            swapRB=True,
            crop=False
        )
        return blob
    
    def postprocess(self, outputs: np.ndarray, frame_shape: Tuple[int, int]) -> List[dict]:
        """
        Post-process YOLO outputs
        
        Args:
            outputs: Raw YOLO output
            frame_shape: Original frame shape (height, width)
        
        Returns:
            List of detections with format:
            {
                'class_id': int,
                'class_name': str,
                'confidence': float,
                'box': (x, y, w, h)
            }
        """
        img_height, img_width = frame_shape
        
        # Handle 3D tensor from ONNX export
        if len(outputs.shape) == 3:
            outputs = outputs[0]
        
        boxes = []
        confidences = []
        class_ids = []
        
        # Calculate scaling factors
        x_factor = img_width / self.input_size
        y_factor = img_height / self.input_size
        
        # Parse detections
        for row in outputs:
            confidence = row[4]
            
            if confidence >= self.confidence_threshold:
                classes_scores = row[5:]
                class_id = np.argmax(classes_scores)
                
                if classes_scores[class_id] >= self.confidence_threshold:
                    # Get box coordinates (center_x, center_y, width, height)
                    cx, cy, w, h = row[0:4]
                    
                    # Convert to corner coordinates
                    left = int((cx - w / 2) * x_factor)
                    top = int((cy - h / 2) * y_factor)
                    width = int(w * x_factor)
                    height = int(h * y_factor)
                    
                    boxes.append([left, top, width, height])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Apply Non-Maximum Suppression
        indices = cv2.dnn.NMSBoxes(
            boxes,
            confidences,
            self.confidence_threshold,
            self.nms_threshold
        )
        
        # Format results
        detections = []
        
        if len(indices) > 0:
            # Handle both old and new OpenCV NMS output formats
            indices_flat = np.array(indices).flatten()
            
            for i in indices_flat:
                detection = {
                    'class_id': class_ids[i],
                    'class_name': self.classes[class_ids[i]],
                    'confidence': confidences[i],
                    'box': boxes[i]  # (x, y, w, h)
                }
                detections.append(detection)
        
        return detections
    
    def detect(self, frame: np.ndarray) -> List[dict]:
        """
        Detect objects in frame
        
        Args:
            frame: Input image (BGR format)
        
        Returns:
            List of detections
        """
        # Preprocess
        blob = self.preprocess(frame)
        
        # Run inference
        self.net.setInput(blob)
        outputs = self.net.forward()
        
        # Post-process
        detections = self.postprocess(outputs[0], frame.shape[:2])
        
        return detections
    
    def filter_target_classes(self, detections: List[dict]) -> List[dict]:
        """
        Filter detections to only include target classes
        
        Args:
            detections: List of all detections
        
        Returns:
            List of detections matching target classes
        """
        target_classes_lower = [c.lower() for c in config.TARGET_CLASSES]
        
        filtered = [
            det for det in detections
            if det['class_name'].lower() in target_classes_lower
        ]
        
        return filtered


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_detector() -> ObjectDetector:
    """
    Factory function to create detector with config settings
    """
    return ObjectDetector(config.YOLO_MODEL_PATH)
