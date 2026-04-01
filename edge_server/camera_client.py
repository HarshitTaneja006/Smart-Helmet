"""
camera_client.py
MJPEG stream reader for ESP32-CAM + vibration trigger
"""

import cv2
import numpy as np
import urllib.request
import requests
import threading
import logging
import time
import config

logger = logging.getLogger(__name__)


class ESP32CameraClient:
    """
    Reads MJPEG stream from ESP32-CAM in a background thread.
    Always holds the latest frame — no per-frame HTTP overhead.
    """

    def __init__(self):
        self.stream_url = config.ESP32_STREAM_URL
        self.vibrate_url = config.ESP32_VIBRATE_URL
        self.status_url = config.ESP32_STATUS_URL
        self.timeout = config.ESP32_TIMEOUT

        self.frame = None
        self.status = False
        self.running = True

        self._thread = threading.Thread(target=self._stream_loop, daemon=True)
        self._thread.start()

        logger.info(f"Camera client started (stream: {self.stream_url})")

    def _stream_loop(self):
        """Background thread: continuously read MJPEG stream."""
        while self.running:
            try:
                stream = urllib.request.urlopen(self.stream_url, timeout=self.timeout)
                bytes_data = b''
                while self.running:
                    chunk = stream.read(4096)
                    if not chunk:
                        break
                    bytes_data += chunk
                    # Find JPEG start (0xFFD8) and end (0xFFD9) markers
                    a = bytes_data.find(b'\xff\xd8')
                    b = bytes_data.find(b'\xff\xd9')
                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b + 2]
                        bytes_data = bytes_data[b + 2:]
                        if len(jpg) > 0:
                            frame = cv2.imdecode(
                                np.frombuffer(jpg, dtype=np.uint8),
                                cv2.IMREAD_COLOR
                            )
                            if frame is not None:
                                self.status = True
                                self.frame = frame
            except Exception as e:
                self.status = False
                logger.debug(f"Stream read error: {e}")
                if self.running:
                    time.sleep(1.0)

    def get_frame(self):
        """Return (success, frame) — latest frame from stream."""
        return self.status, self.frame

    def trigger_vibration(self):
        """Trigger vibration motor on ESP32."""
        try:
            response = requests.get(self.vibrate_url, timeout=self.timeout)
            if response.status_code == 200:
                logger.info("Vibration motor triggered")
                return True
            return False
        except Exception as e:
            logger.error(f"Vibration trigger failed: {e}")
            return False

    def test_connection(self):
        """Test if ESP32-CAM is reachable."""
        logger.info("Testing ESP32 connection...")
        # Wait up to 5 seconds for first frame
        for _ in range(50):
            if self.status and self.frame is not None:
                h, w = self.frame.shape[:2]
                logger.info(f"ESP32 connected ({w}x{h})")
                return True
            time.sleep(0.1)

        logger.error(f"Cannot connect to ESP32 at {self.stream_url}")
        return False

    def release(self):
        """Stop background thread."""
        self.running = False


def create_camera_client():
    return ESP32CameraClient()
