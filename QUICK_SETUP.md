# ⚡ QUICK SETUP GUIDE

**Get your Smart Safety Helmet running in 10 minutes!**

---

## 📋 Prerequisites

- ESP32-CAM module
- Arduino IDE installed
- Python 3.8+ installed
- WiFi network (2.4GHz)
- YOLOv5s ONNX model (download link below)

---

## 🚀 Setup Steps

### 1️⃣ Flash ESP32-CAM (5 minutes)

```bash
# 1. Open Arduino IDE
# 2. Install ESP32 board support:
#    File → Preferences → Additional Board Manager URLs:
#    https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json

# 3. Install board:
#    Tools → Board → Boards Manager → "ESP32" → Install

# 4. Open firmware:
#    esp32_firmware/smart_helmet_cam/smart_helmet_cam.ino

# 5. Edit WiFi credentials (lines 23-24):
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

# 6. Upload:
#    Tools → Board → "AI Thinker ESP32-CAM"
#    Tools → Port → Select COM port
#    Upload button

# 7. Get IP address:
#    Tools → Serial Monitor (115200 baud)
#    Copy the IP address shown
```

---

### 2️⃣ Setup Edge Server (3 minutes)

```bash
# 1. Install Python dependencies
cd edge_server
pip install -r requirements.txt

# 2. Download YOLOv5 model (choose one):

# Option A: Direct download (~14MB)
mkdir -p ../models
cd ../models
# Windows (PowerShell):
Invoke-WebRequest -Uri "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.onnx" -OutFile "yolov5s.onnx"
# Linux/Mac:
wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.onnx

# Option B: Use your existing yolov5s.onnx file
# Just copy it to: models/yolov5s.onnx

# 3. Configure ESP32 IP
cd ../edge_server
# Edit config.py line 13:
ESP32_IP = "192.168.1.XXX"  # Your ESP32 IP from step 1
```

---

### 3️⃣ Run System (2 minutes)

```bash
# 1. Make sure ESP32-CAM is powered on

# 2. Run edge server
cd edge_server
python main.py

# 3. You should see:
#    ✓ ESP32 is online
#    ✓ Camera is working
#    Video window opens

# 4. Test fall detection:
#    - Hold phone/cup in front of camera
#    - Wait for green box
#    - DROP it
#    - Red alert should appear + motor vibrates
```

---

## 🔧 Hardware Connections

### Vibration Motor Wiring

**Simple (Direct Connection):**
```
GPIO 12 ──> Motor (+)
GND     ──> Motor (-)
```

**Recommended (With Transistor):**
```
GPIO 12 ──[ 1kΩ resistor ]──> NPN Transistor Base (2N2222)
GND     ──> Transistor Emitter
Motor (-) ──> Transistor Collector
Motor (+) ──> 5V
```

---

## ✅ Testing Checklist

- [ ] ESP32-CAM boots and connects to WiFi
- [ ] Serial Monitor shows IP address
- [ ] Edge server connects to ESP32
- [ ] Video window opens showing camera feed
- [ ] Objects detected (green boxes appear)
- [ ] Dropping object triggers red alert
- [ ] Vibration motor activates

---

## 🐛 Common Issues

### "CANNOT CONNECT TO ESP32-CAM"
```python
# Fix: Update ESP32 IP in config.py
ESP32_IP = "192.168.1.100"  # Use YOUR ESP32 IP
```

### "Model file not found"
```bash
# Fix: Check model path
ls models/yolov5s.onnx  # Should exist
# If not, re-download from step 2
```

### "No objects detected"
```python
# Fix: Lower confidence in config.py
DETECTION_CONFIDENCE = 0.15  # Try lower value
```

### "Fall detection not triggering"
```python
# Fix: Lower threshold in config.py
FALL_VELOCITY_THRESHOLD = 10.0  # More sensitive
```

---

## 📞 Need Help?

1. Check main README.md for detailed docs
2. Review Troubleshooting section
3. Check ESP32 Serial Monitor for errors
4. Test connection: `ping YOUR_ESP32_IP`

---

**Total Setup Time: ~10 minutes**
**You're ready to go! 🚀**
