# Smart Safety Helmet - ESP32-CAM + Edge Server

Hybrid fall detection system: MOG2 motion detection (edge server) + accelerometer impact detection (ESP32-CAM).

## Project Structure

```
├── esp32_firmware/              # Arduino code for ESP32-CAM
│   └── smart_helmet_cam_with_impact/
│       ├── smart_helmet_cam_with_impact.ino  # Main sketch
│       ├── camera_handler.h                    # Camera initialization
│       ├── accelerometer_handler.h             # MPU6050 accelerometer
│       ├── buzzer_controller.h                 # Alert buzzer control
│       └── motor_controller.h                  # Vibration motor control
│
├── edge_server/                 # Python motion detection server
│   ├── main.py                  # Entry point - MOG2 motion detection
│   ├── config.py                # Configuration (sensitivity, thresholds)
│   ├── camera_client.py         # ESP32 MJPEG stream client
│   ├── fall_tracker.py          # Object tracking with optical flow
│   ├── alert_manager.py         # Visual & haptic alert system
│   ├── requirements.txt          # Python dependencies
│   └── __pycache__/             # Compiled Python cache (ignore)
│
└── README.md                    # This file
```

## System Architecture

```
┌─────────────────┐                     ┌──────────────────────┐
│   ESP32-CAM     │   ──── WiFi ────>   │   Laptop/PC          │
│                 │                     │   (Edge Server)      │
│  - Capture      │                     │                      │
│  - MJPEG        │                     │  - MOG2 Background   │
│    Streaming    │                     │    Subtraction       │
│  - Impact       │                     │  - Centroid Tracking │
│    Detection    │                     │  - Optical Flow      │
│  - Vibration    │                     │  - Fall Detection    │
│    Motor        │                     │  - Alert Manager     │
│  - Impact       │   <─── WiFi ──────  │                      │
│    Buzzer       │   (Alerts/Control)  │                      │
└─────────────────┘                     └──────────────────────┘
```

### Component Responsibilities:

**ESP32-CAM (Firmware):**
- ✅ Capture images from OV2640 camera (640x480 MJPEG streaming)
- ✅ Serve MJPEG video stream via HTTP `/stream`
- ✅ Monitor accelerometer (MPU6050) for impacts
- ✅ Trigger buzzer on high-impact events (4.0G threshold)
- ✅ Control vibration motor via HTTP `/vibrate`
- ✅ Operate independently (no network dependency for impact alerts)

**Edge Server (Laptop/PC):**
- ✅ Stream images from ESP32-CAM over WiFi
- ✅ Detect motion using MOG2 background subtraction (class-agnostic)
- ✅ Compensate for helmet camera motion via optical flow
- ✅ Track falling objects using centroid-based tracking
- ✅ Measure vertical velocity to detect falls
- ✅ Trigger alerts (red screen overlay + motor) when fall detected
- ✅ Display real-time video with debug overlays

## Quick Start

### Step 1: Setup ESP32-CAM

1. **Install Arduino IDE** (if not already installed)
   - Download from: https://www.arduino.cc/en/software

2. **Install ESP32 Board Support**
   - File → Preferences
   - Add to "Additional Board Manager URLs":
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
   - Tools → Board → Boards Manager → Search "esp32" → Install

3. **Flash ESP32-CAM Firmware**
   - Open `esp32_firmware/smart_helmet_cam/smart_helmet_cam.ino`
   - Edit WiFi credentials:
     ```cpp
     const char* WIFI_SSID = "Your_WiFi_Name";
     const char* WIFI_PASSWORD = "Your_WiFi_Password";
     ```
   - Tools → Board → "AI Thinker ESP32-CAM"
   - Tools → Port → Select your COM port
   - Click Upload

4. **Get ESP32 IP Address**
   - Open Serial Monitor (115200 baud)
   - ESP32 will print its IP address on boot:
     ```
     =====================================
     COPY THIS IP ADDRESS:
     >>> 192.168.1.100 <<<
     =====================================
     ```

### Step 2: Setup Edge Server

1. **Install Python Requirements**
   ```bash
   cd edge_server
   pip install -r requirements.txt
   ```

2. **Configure ESP32 IP Address**
   - Edit `edge_server/config.py`
   - Update ESP32_IP with your ESP32's IP:
     ```python
     ESP32_IP = "192.168.1.100"  # Change this!
     ```

3. **Run Edge Server**
   ```bash
   python main.py
   ```

---

## Usage

### Running the System

1. **Power on ESP32-CAM**
   - Wait for WiFi connection (~5 seconds)
   - Check Serial Monitor for IP address

2. **Start Edge Server**
   ```bash
   cd edge_server
   python main.py
   ```

3. **Test Connection**
   - Edge server will test ESP32 connection on startup
   - If successful, video window will open

4. **Test Fall Detection**
   - Point camera at an object (phone, cup, bottle, etc.)
   - Watch for green bounding box (object being tracked)
   - **Drop the object** straight down quickly
   - Alert should trigger (red overlay + vibration motor)

### Keyboard Controls

- **Q** - Quit application
- **R** - Reset fall tracker

## Configuration

All settings are in `edge_server/config.py`:

### ESP32 Settings
```python
ESP32_IP = "192.168.1.100"  # ESP32-CAM IP address
```

### Fall Detection Settings
```python
FALL_VELOCITY_THRESHOLD = 15.0   # Pixels per frame (lower = more sensitive)
MIN_CONSECUTIVE_FRAMES = 2       # Frames to confirm fall
ALERT_COOLDOWN = 3.0             # Seconds between alerts
MAX_TRACKING_DISTANCE = 200      # Max pixel distance to match objects
```

### Motion Detection Settings (MOG2)
```python
MIN_CONTOUR_AREA = 1500          # Minimum object size (pixels²)
MAX_CONTOUR_AREA = 200000        # Maximum object size (pixels²)
LEARNING_RATE = 0.005            # Background model learning rate
```

### Sensitivity Presets
```python
SENSITIVITY_PRESETS = {
    'LOW':    {'min_area': 2500, 'velocity': 25.0, 'consecutive': 3},
    'MEDIUM': {'min_area': 1500, 'velocity': 15.0, 'consecutive': 2},
    'HIGH':   {'min_area': 800,  'velocity': 8.0,  'consecutive': 2},
}
# Cycle presets with 'S' key during execution
```

## Hardware Setup

### ESP32-CAM Wiring

**Vibration Motor Connection:**
```
ESP32-CAM GPIO 12 ──> Motor (+) or Transistor Base
         GND     ──> Motor (-) or Transistor Emitter
         5V      ──> Motor VCC (via transistor if needed)
```

**Recommended: Use NPN Transistor (2N2222)**
```
GPIO 12 ──[ 1kΩ ]──> Base
                     Emitter ──> GND
                     Collector ──> Motor (-) ──> Motor (+) ──> 5V
```

### Power Supply

- **ESP32-CAM**: 5V @ 500mA minimum (use USB power adapter)
- **Vibration Motor**: Typically 3-5V @ 50-100mA

## Performance

### ESP32-CAM (Capture Only)
- **FPS**: ~10-15 FPS (640x480 JPEG)
- **Latency**: ~100ms per frame
- **Memory**: ~200KB RAM used
- **Power**: ~500mA @ 5V

### Edge Server (Laptop i5)
- **FPS**: 20-30 FPS (with YOLOv5s)
- **Detection Latency**: ~50ms per frame
- **Total Latency**: ~150-200ms (capture + inference + alert)
- **CPU Usage**: ~30-50%

## Testing

### Test ESP32 Camera
```bash
# Test if ESP32 is accessible
curl http://192.168.1.100/status

# View camera feed in browser
http://192.168.1.100/capture

# Test vibration motor
curl http://192.168.1.100/vibrate
```

### Test Edge Server Components
```bash
cd edge_server

# Test camera connection
python -c "from camera_client import create_camera_client; c = create_camera_client(); print(c.test_connection())"

# Test ONNX model loading
python -c "from object_detector import create_detector; d = create_detector(); print('Model loaded')"
```

## Troubleshooting

### ESP32 Not Connecting to WiFi
- Check SSID and password in Arduino sketch
- Ensure WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
- Check Serial Monitor for error messages

### Edge Server Cannot Connect to ESP32
```
CANNOT CONNECT TO ESP32-CAM
```
**Solutions:**
1. Verify ESP32 IP address in `config.py`
2. Ping ESP32: `ping 192.168.1.100`
3. Check if ESP32 and laptop are on same network
4. Disable firewall temporarily to test

### No Objects Detected
- Lower confidence threshold in `config.py`:
  ```python
  DETECTION_CONFIDENCE = 0.15  # Try lower value
  ```
- Check if object is in TARGET_CLASSES list
- Improve lighting conditions

### Fall Detection Not Triggering
- Lower velocity threshold:
  ```python
  FALL_VELOCITY_THRESHOLD = 10.0  # More sensitive
  ```
- Drop object from higher position
- Ensure object is being tracked (green box visible)

### Low FPS
- Lower MOG2 LEARNING_RATE for faster background adaptation
- Reduce MIN_CONTOUR_AREA to skip small objects
- Close other applications consuming CPU
- Ensure WiFi signal is strong between ESP32 and laptop

## File Descriptions

### ESP32 Firmware Files

- **smart_helmet_cam_with_impact.ino** - Main Arduino sketch, HTTP server, MJPEG streaming, impact detection
- **camera_handler.h** - OV2640 camera initialization and MJPEG server
- **accelerometer_handler.h** - MPU6050 I2C driver for impact detection
- **buzzer_controller.h** - Piezo buzzer control for impact alerts
- **motor_controller.h** - GPIO control for vibration motor

### Edge Server Files

- **main.py** - Main application loop, MOG2 background subtraction pipeline, real-time video display
- **config.py** - All configuration settings (sensitivity, thresholds, ESP32 IP)
- **camera_client.py** - MJPEG stream reader and HTTP client for ESP32 communication
- **fall_tracker.py** - Centroid-based object tracking with optical flow ego-motion compensation
- **alert_manager.py** - Visual overlay rendering and vibration motor triggering

## References

- **YOLOv5**: https://github.com/ultralytics/yolov5
- **ESP32-CAM**: https://github.com/espressif/arduino-esp32
- **OpenCV**: https://opencv.org/

## License

This project is for educational purposes.

**Good luck with your project! 🚀**
