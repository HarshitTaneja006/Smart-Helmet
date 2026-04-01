"""
main.py
Smart Safety Helmet - Edge Server
Motion-based fall detection using MOG2 background subtraction.
Detects ANY falling object (class-agnostic, no AI model needed).
"""

import cv2
import numpy as np
import logging
import time
import sys

import config
from camera_client import create_camera_client
from fall_tracker import create_fall_tracker
from alert_manager import create_alert_manager

# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging():
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    level = getattr(logging, config.LOG_LEVEL.upper())
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)]
    )

# =============================================================================
# MAIN APPLICATION
# =============================================================================

class SmartHelmetEdgeServer:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.logger.info("=" * 70)
        self.logger.info("Smart Safety Helmet - Motion-Based Fall Detection")
        self.logger.info("=" * 70)

        # --- MOG2 Background Subtractor ---
        self.logger.info("Initializing motion detector (MOG2)...")
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=50,
            detectShadows=True
        )
        self.kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self.kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        self.logger.info("Motion detector ready")

        # --- Components ---
        self.camera_client = create_camera_client()
        self.fall_tracker = create_fall_tracker()
        self.alert_manager = create_alert_manager()

        # --- Runtime state ---
        self.frame_count = 0
        self.min_contour_area = config.MIN_CONTOUR_AREA
        self.current_sensitivity = config.CURRENT_SENSITIVITY

        self.logger.info("=" * 70)

    def test_connection(self):
        self.logger.info("Testing ESP32-CAM connection...")
        return self.camera_client.test_connection()

    def process_frame(self, frame):
        """
        Full pipeline: resize -> ego-motion -> MOG2 -> contours -> tracker.
        Returns (display_frame, fg_mask, fall_detected, blob_count).
        """
        h, w = frame.shape[:2]
        if w != config.FRAME_WIDTH or h != config.FRAME_HEIGHT:
            frame = cv2.resize(frame, (config.FRAME_WIDTH, config.FRAME_HEIGHT))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # --- Ego-motion estimation (optical flow) ---
        ego_motion_y, camera_is_moving = self.fall_tracker.estimate_ego_motion(gray)

        # --- Background subtraction ---
        lr = config.CAMERA_MOTION_FAST_LEARN if camera_is_moving else config.LEARNING_RATE
        fg_mask = self.bg_subtractor.apply(frame, learningRate=lr)

        # Remove shadows (MOG2 marks shadows as 127, foreground as 255)
        _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

        # Morphological cleanup
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel_open)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, self.kernel_close)

        # --- Global motion check ---
        fg_ratio = np.count_nonzero(fg_mask) / (config.FRAME_WIDTH * config.FRAME_HEIGHT)
        if fg_ratio > config.CAMERA_MOTION_RATIO_THRESHOLD:
            camera_is_moving = True

        # --- Find and filter contours ---
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        valid_contours = []
        if not camera_is_moving:
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if self.min_contour_area < area < config.MAX_CONTOUR_AREA:
                    valid_contours.append(cnt)

        # --- Update tracker ---
        current_time = time.time()
        fall_detected, tracked = self.fall_tracker.update(
            valid_contours, current_time, ego_motion_y
        )

        # --- Draw tracked objects ---
        for obj_id, obj in tracked.items():
            if obj['missed'] > 0:
                continue

            x, y, bw, bh = obj['rect']
            fall_count = obj['fall_count']

            if fall_count >= config.MIN_CONSECUTIVE_FRAMES - 1:
                color = config.COLOR_ALERT       # Red
            elif fall_count > 0:
                color = config.COLOR_FALLING      # Orange
            else:
                color = config.COLOR_TRACKED      # Green

            cv2.rectangle(frame, (x, y), (x + bw, y + bh), color, 2)

            label = f"ID:{obj_id}"
            if fall_count > 0:
                label += f" FALLING({fall_count})"
            cv2.putText(frame, label, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Draw motion trail
            trail = obj['trail']
            for i in range(1, len(trail)):
                alpha = i / len(trail)
                thickness = max(1, int(alpha * 3))
                cv2.line(frame, trail[i - 1], trail[i], color, thickness)

        # Camera motion overlay
        if camera_is_moving:
            cv2.putText(frame, "CAMERA MOVING - detection paused",
                        (10, config.FRAME_HEIGHT - 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

        # Alert overlay
        if self.alert_manager.is_alert_active():
            frame = self.alert_manager.render_alert(frame)

        return frame, fg_mask, fall_detected, len(valid_contours)

    def run(self):
        self.logger.info("Starting main loop...")
        self.logger.info("Controls: Q=Quit  D=Debug  S=Sensitivity  R=Reset")
        self.logger.info("=" * 70)

        fps_time = time.time()
        fps_counter = 0
        fps_display = 0
        sensitivity_keys = list(config.SENSITIVITY_PRESETS.keys())
        current_sens_idx = sensitivity_keys.index(self.current_sensitivity)

        try:
            while True:
                success, frame = self.camera_client.get_frame()
                if not success or frame is None:
                    time.sleep(0.01)
                    continue

                self.frame_count += 1

                # --- Process ---
                processed, fg_mask, fall_detected, blob_count = self.process_frame(frame)

                # --- Handle fall ---
                if fall_detected:
                    self.logger.warning("FALL DETECTED! Activating alerts...")
                    self.alert_manager.trigger_alert(self.camera_client)

                # --- FPS ---
                fps_counter += 1
                if time.time() - fps_time > 1.0:
                    fps_display = fps_counter
                    fps_counter = 0
                    fps_time = time.time()

                # --- Status overlay ---
                y_offset = 30
                tracked_count = len(self.fall_tracker.get_tracked_objects())
                for item in [
                    f"FPS: {fps_display}",
                    f"Blobs: {blob_count}",
                    f"Tracked: {tracked_count}",
                    f"Sensitivity: {self.current_sensitivity}",
                    f"Debug: {'ON' if config.DEBUG_MODE else 'OFF'}"
                ]:
                    cv2.putText(processed, item, (10, y_offset),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    y_offset += 25

                # Instructions
                cv2.putText(processed,
                            "Q:Quit | D:Debug | S:Sensitivity | R:Reset",
                            (10, config.FRAME_HEIGHT - 35),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(processed,
                            "GREEN=Tracked | ORANGE=Falling | RED=Alert",
                            (10, config.FRAME_HEIGHT - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                # --- Display ---
                if config.SHOW_VIDEO:
                    cv2.imshow(config.WINDOW_NAME, processed)

                if config.DEBUG_MODE:
                    cv2.imshow('Motion Mask (Debug)',
                               cv2.cvtColor(fg_mask, cv2.COLOR_GRAY2BGR))

                # --- Keyboard ---
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    self.logger.info("Quit requested")
                    break
                elif key == ord('r'):
                    self.logger.info("Resetting tracker...")
                    self.fall_tracker.reset()
                elif key == ord('d'):
                    config.DEBUG_MODE = not config.DEBUG_MODE
                    self.logger.info(f"Debug mode: {'ON' if config.DEBUG_MODE else 'OFF'}")
                    if not config.DEBUG_MODE:
                        cv2.destroyWindow('Motion Mask (Debug)')
                elif key == ord('s'):
                    current_sens_idx = (current_sens_idx + 1) % len(sensitivity_keys)
                    self.current_sensitivity = sensitivity_keys[current_sens_idx]
                    preset = config.SENSITIVITY_PRESETS[self.current_sensitivity]
                    self.min_contour_area = preset['min_area']
                    config.FALL_VELOCITY_THRESHOLD = preset['velocity']
                    config.MIN_CONSECUTIVE_FRAMES = preset['consecutive']
                    self.logger.info(
                        f"Sensitivity: {self.current_sensitivity} "
                        f"(area>{self.min_contour_area}, "
                        f"vel>{config.FALL_VELOCITY_THRESHOLD}, "
                        f"frames>={config.MIN_CONSECUTIVE_FRAMES})"
                    )

        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        finally:
            self.cleanup()

    def cleanup(self):
        self.camera_client.release()
        cv2.destroyAllWindows()
        self.logger.info("Cleanup complete")


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        app = SmartHelmetEdgeServer()

        if not app.test_connection():
            logger.error("=" * 70)
            logger.error("CANNOT CONNECT TO ESP32-CAM")
            logger.error(f"Stream URL: {config.ESP32_STREAM_URL}")
            logger.error("Check: 1) ESP32 powered on  2) Same WiFi  3) Correct IP in config.py")
            logger.error("=" * 70)
            return 1

        app.run()
        return 0

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
