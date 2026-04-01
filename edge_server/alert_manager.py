"""
alert_manager.py
Manages fall detection alerts (visual, audio, motor)
"""

import cv2
import numpy as np
import logging
import time
from typing import Optional
import config

logger = logging.getLogger(__name__)

class AlertManager:
    """
    Manages fall detection alerts
    
    Methods:
        trigger_alert(camera_client) -> bool
        render_alert(frame) -> np.ndarray
        is_alert_active() -> bool
    """
    
    def __init__(self):
        """
        Initialize alert manager
        """
        self.alert_duration = config.ALERT_DURATION
        self.alert_start_time = None
        self.alert_count = 0
        
        logger.info("Alert Manager initialized")
        logger.info(f"Alert duration: {self.alert_duration}s")
    
    def trigger_alert(self, camera_client) -> bool:
        """
        Trigger fall alert
        
        Args:
            camera_client: ESP32CameraClient instance
        
        Returns:
            bool: True if alert triggered successfully
        """
        self.alert_start_time = time.time()
        self.alert_count += 1
        
        logger.warning(f"🚨 ALERT #{self.alert_count} TRIGGERED!")
        
        # Trigger vibration motor on ESP32
        success = camera_client.trigger_vibration()
        
        if success:
            logger.info("✓ Vibration motor activated")
        else:
            logger.error("✗ Failed to activate vibration motor")
        
        return success
    
    def is_alert_active(self) -> bool:
        """
        Check if alert is currently active
        
        Returns:
            bool: True if alert is active
        """
        if self.alert_start_time is None:
            return False
        
        elapsed = time.time() - self.alert_start_time
        
        if elapsed > self.alert_duration:
            self.alert_start_time = None
            return False
        
        return True
    
    def render_alert(self, frame: np.ndarray) -> np.ndarray:
        """
        Render alert overlay on frame
        
        Args:
            frame: Input frame
        
        Returns:
            Frame with alert overlay
        """
        if not self.is_alert_active():
            return frame
        
        height, width = frame.shape[:2]
        
        # Create red overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 255), -1)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
        
        # Draw red border
        border_thickness = 30
        cv2.rectangle(frame, (0, 0), (width, height), 
                     config.COLOR_ALERT, border_thickness)
        
        # Draw "DANGER!" text
        text = "DANGER!"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 4
        thickness = 10
        
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_x = (width - text_width) // 2
        text_y = (height + text_height) // 2
        
        # Black outline
        cv2.putText(frame, text, (text_x, text_y), font, font_scale,
                   (0, 0, 0), thickness + 6, cv2.LINE_AA)
        # White text
        cv2.putText(frame, text, (text_x, text_y), font, font_scale,
                   (255, 255, 255), thickness, cv2.LINE_AA)
        
        # Countdown timer
        remaining = self.alert_duration - (time.time() - self.alert_start_time)
        countdown_text = f"{remaining:.1f}s"
        cv2.putText(frame, countdown_text, (width//2 - 50, height - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4)
        
        # Alert counter
        counter_text = f"Alert #{self.alert_count}"
        cv2.putText(frame, counter_text, (20, height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        return frame


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_alert_manager() -> AlertManager:
    """
    Factory function to create alert manager
    """
    return AlertManager()
