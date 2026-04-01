# config.py
# =============================================================================
# Smart Safety Helmet - Edge Server Configuration
# =============================================================================

# =============================================================================
# ESP32-CAM SETTINGS
# =============================================================================

# CHANGE THIS TO YOUR ESP32-CAM IP ADDRESS
# (Check Arduino Serial Monitor after ESP32 boots)
ESP32_IP = "10.107.169.207"  # UPDATE THIS!

# ESP32 Endpoints
ESP32_STREAM_URL = f"http://{ESP32_IP}:81/stream"
ESP32_VIBRATE_URL = f"http://{ESP32_IP}/vibrate"
ESP32_STATUS_URL = f"http://{ESP32_IP}/status"

# Network timeouts
ESP32_TIMEOUT = 5.0  # seconds

# =============================================================================
# MOTION DETECTION SETTINGS (MOG2 Background Subtraction)
# =============================================================================

# Minimum contour area (pixels^2) - ignore blobs smaller than this (noise)
MIN_CONTOUR_AREA = 1500

# Maximum contour area (pixels^2) - ignore blobs larger than this (whole-frame noise)
MAX_CONTOUR_AREA = 200000

# Background model learning rate (lower = more stable background)
LEARNING_RATE = 0.005

# =============================================================================
# FALL DETECTION SETTINGS
# =============================================================================

# Vertical velocity threshold (pixels per frame)
# Object must move downward by at least this many pixels
# Lower values = more sensitive
FALL_VELOCITY_THRESHOLD = 15.0

# Minimum consecutive frames to confirm fall
MIN_CONSECUTIVE_FRAMES = 2

# Alert duration (seconds)
ALERT_DURATION = 5.0

# Alert cooldown period (seconds) - prevents repeated alerts
ALERT_COOLDOWN = 3.0

# Maximum tracking distance (pixels) - match blobs between frames
MAX_TRACKING_DISTANCE = 200

# Remove tracked object after this many missed frames
MAX_MISSED_FRAMES = 5

# =============================================================================
# EGO-MOTION COMPENSATION (helmet camera moves)
# =============================================================================

# If more than this fraction of the frame is foreground, assume camera motion
CAMERA_MOTION_RATIO_THRESHOLD = 0.25

# Faster learning rate when camera is moving (adapts background quickly)
CAMERA_MOTION_FAST_LEARN = 0.05

# =============================================================================
# DISPLAY SETTINGS
# =============================================================================

# Show video window
SHOW_VIDEO = True

# Display window name
WINDOW_NAME = "Smart Safety Helmet - Edge Server"

# Frame dimensions for processing
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Box colors (BGR format)
COLOR_TRACKED = (0, 255, 0)      # Green - tracked objects
COLOR_FALLING = (0, 165, 255)    # Orange - fall building
COLOR_ALERT = (0, 0, 255)        # Red - fall detected / alert imminent

# Debug mode - shows motion mask and per-object velocity info
DEBUG_MODE = True

# =============================================================================
# SENSITIVITY PRESETS (cycle with 'S' key)
# =============================================================================

SENSITIVITY_PRESETS = {
    'LOW':    {'min_area': 2500, 'velocity': 25.0, 'consecutive': 3},
    'MEDIUM': {'min_area': 1500, 'velocity': 15.0, 'consecutive': 2},
    'HIGH':   {'min_area': 800,  'velocity': 8.0,  'consecutive': 2},
}
CURRENT_SENSITIVITY = 'MEDIUM'

# =============================================================================
# LOGGING SETTINGS
# =============================================================================

LOG_LEVEL = "INFO"
LOG_TO_CONSOLE = True
LOG_TO_FILE = False
LOG_FILE_PATH = "logs/edge_server.log"
