# 🎯 Smart Safety Helmet - ESP32-CAM + Edge Server

**Modular, Production-Ready Fall Detection System**

---

## 📁 Project Structure

```
smart-helmet-esp32/
├── esp32_firmware/              # Arduino code for ESP32-CAM
│   ├── smart_helmet_cam/
│   │   ├── smart_helmet_cam.ino    # Main sketch
│   │   ├── camera_handler.h         # Camera initialization
│   │   └── motor_controller.h       # Vibration motor control
│   └── README.md
│
├── edge_server/                 # Python inference server
│   ├── main.py                  # Entry point
│   ├── config.py                # Configuration
│   ├── camera_client.py         # ESP32 communication
│   ├── object_detector.py       # YOLOv5 ONNX inference
│   ├── fall_tracker.py          # Fall detection logic
│   ├── alert_manager.py         # Alert system
│   └── requirements.txt
│
├── models/                      # AI models
│   └── yolov5s.onnx            # YOLOv5 ONNX model
│
└── README.md                    # This file
```

---

## 🎯 System Architecture

```
┌─────────────────┐                    ┌──────────────────────┐
│   ESP32-CAM     │ ──── WiFi ────>    │   Laptop/PC          │
│                 │                     │   (Edge Server)      │
│  - Capture      │                     │                      │
│  - Serve Image  │                     │  - YOLOv5 Inference  │
│  - Vibration    │                     │  - Fall Detection    │
│    Motor        │                     │  - Alert Logic       │
│                 │ <─── WiFi ──────    │                      │
│                 │   (Alert Trigger)   │                      │
└─────────────────┘                    └──────────────────────┘
```

### Component Responsibilities:

**ESP32-CAM (Firmware):**
- ✅ Capture images from OV2640 camera (640x480 @ ~10 FPS)
- ✅ Serve images via HTTP endpoint `/capture`
- ✅ Control vibration motor via HTTP endpoint `/vibrate`
- ✅ Simple, stable, **no AI processing**

**Edge Server (Laptop/PC):**
- ✅ Fetch images from ESP32-CAM over WiFi
- ✅ Run YOLOv5 ONNX inference using OpenCV DNN
- ✅ Track objects and detect falling motion
- ✅ Trigger alerts (visual + motor) when fall detected
- ✅ Display real-time video with overlays

---

## 🚀 Quick Start

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

2. **Download YOLOv5 ONNX Model**
   ```bash
   # Create models directory
   mkdir -p ../models
   
   # Download YOLOv5s ONNX model (~14MB)
   # Option 1: From GitHub Releases
   wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.onnx
   mv yolov5s.onnx ../models/
   
   # Option 2: Convert from PyTorch (if you have YOLOv5 installed)
   # python path/to/yolov5/export.py --weights yolov5s.pt --include onnx
   ```

3. **Configure ESP32 IP Address**
   - Edit `edge_server/config.py`
   - Update ESP32_IP with your ESP32's IP:
     ```python
     ESP32_IP = "192.168.1.100"  # Change this!
     ```

4. **Run Edge Server**
   ```bash
   python main.py
   ```

---

## 🎮 Usage

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
   - Hold an object (phone, cup, etc.) in front of camera
   - Wait for green bounding box to appear
   - **Drop the object** straight down
   - Alert should trigger (red screen + vibration motor)

### Keyboard Controls

- **Q** - Quit application
- **R** - Reset fall tracker

---

## ⚙️ Configuration

All settings are in `edge_server/config.py`:

### ESP32 Settings
```python
ESP32_IP = "192.168.1.100"  # ESP32-CAM IP address
```

### Fall Detection Settings
```python
FALL_VELOCITY_THRESHOLD = 15.0   # Pixels per frame
MIN_CONSECUTIVE_FRAMES = 2       # Frames to confirm fall
ALERT_COOLDOWN = 2.0             # Seconds between alerts
```

### Model Settings
```python
YOLO_MODEL_PATH = "../models/yolov5s.onnx"
DETECTION_CONFIDENCE = 0.25      # 0.0-1.0
```

### Target Objects
```python
TARGET_CLASSES = [
    'cell phone', 'cup', 'bottle', 'book', 'scissors',
    'laptop', 'mouse', 'keyboard', # ... etc
]
# NOTE: 'person' is excluded to prevent false alerts
```

---

## 🔧 Hardware Setup

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

---

## 📊 Performance

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

---

## 🧪 Testing

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

---

## 🐛 Troubleshooting

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
- Use YOLOv5n model instead of YOLOv5s (faster but less accurate)
- Reduce YOLO_INPUT_SIZE to 320 in config.py
- Close other applications

---

## 📝 File Descriptions

### ESP32 Firmware Files

- **smart_helmet_cam.ino** - Main Arduino sketch, HTTP server, WiFi
- **camera_handler.h** - OV2640 camera initialization and configuration
- **motor_controller.h** - Vibration motor control class

### Edge Server Files

- **main.py** - Main application loop, orchestrates all components
- **config.py** - All configuration settings (change settings here)
- **camera_client.py** - ESP32 HTTP communication module
- **object_detector.py** - YOLOv5 ONNX inference using OpenCV DNN
- **fall_tracker.py** - Object tracking and fall detection logic
- **alert_manager.py** - Alert rendering and motor trigger

---

## 🔄 Next Steps / Phase 2

- [ ] Add battery power to ESP32-CAM
- [ ] Mount ESP32-CAM on physical helmet
- [ ] Optimize for outdoor lighting conditions
- [ ] Add data logging (fall incidents with timestamps)
- [ ] Implement wireless dashboard (web UI)
- [ ] Add multiple camera support
- [ ] Retrain YOLO for construction-specific objects

---

## 📚 References

- **YOLOv5**: https://github.com/ultralytics/yolov5
- **ESP32-CAM**: https://github.com/espressif/arduino-esp32
- **OpenCV**: https://opencv.org/

---

## 📄 License

This project is for educational purposes.

---

**Good luck with your project! 🚀**
