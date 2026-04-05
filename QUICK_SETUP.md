# Quick Setup Guide

Get your Smart Safety Helmet running in 10 minutes!

## Prerequisites

- ESP32-CAM module
- Arduino IDE installed
- Python 3.8+ installed
- WiFi network (2.4GHz)

## Setup Steps

### 1️⃣ Flash ESP32-CAM (5 minutes)

```bash
# 1. Open Arduino IDE
# 2. Install ESP32 board support:
#    File → Preferences → Additional Board Manager URLs:
#    https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json

# 3. Install board:
#    Tools → Board → Boards Manager → "ESP32" → Install

# 4. Open firmware:
#    esp32_firmware/smart_helmet_cam_with_impact/smart_helmet_cam_with_impact.ino

# 5. Edit WiFi credentials (lines ~23-24):
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

# 6. Upload:
#    Tools → Board → "AI Thinker ESP32-CAM"
#    Tools → Port → Select COM port
#    Click Upload button

# 7. Get IP address:
#    Tools → Serial Monitor (115200 baud)
#    Copy the IP address shown (e.g., "192.168.1.100")
```

---

### 2️⃣ Setup Edge Server (2 minutes)

```bash
# 1. Install Python dependencies
cd edge_server
pip install -r requirements.txt

# 2. Configure ESP32 IP address
# Edit edge_server/config.py (line 12):
ESP32_IP = "192.168.1.XXX"  # Use YOUR ESP32 IP from step 1
```

### 3️⃣ Run System (2 minutes)

```bash
# 1. Make sure ESP32-CAM is powered on

# 2. Run edge server
cd edge_server
python main.py

# 3. You should see:
#    ✓ Connected to ESP32
#    ✓ MJPEG stream starting
#    Video window opens with camera feed

# 4. Test fall detection:
#    - Point camera at an object (phone, cup, bottle, etc.)
#    - Wait for green bounding box to appear
#    - DROP the object quickly downward
#    - Red alert overlay should appear + motor vibrates
```

---

## Hardware Connections

### Vibration Motor Wiring (GPIO 12)

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

## Testing Checklist

- [ ] ESP32-CAM boots and connects to WiFi
- [ ] Serial Monitor shows IP address
- [ ] Edge server connects to ESP32 (no connection errors)
- [ ] Video window opens showing MJPEG camera feed
- [ ] Objects detected (green bounding boxes appear as they move)
- [ ] Dropping object triggers red alert overlay
- [ ] Vibration motor activates (buzzes/vibrates)

---

## Common Issues

### "CANNOT CONNECT TO ESP32-CAM"
```python
# Fix: Verify ESP32 IP in config.py
ESP32_IP = "192.168.1.100"  # Use YOUR ESP32 IP from step 1
# Also check:
# - ESP32 is powered on
# - Same WiFi network as laptop
# - Firewall not blocking connection
```

### "No objects detected / only empty video"
```python
# Fix: Lower motion detection sensitivity
MIN_CONTOUR_AREA = 500  # Lower = detects smaller objects
# See config.py for all motion detection settings
```

### "Fall detection not triggering"
```python
# Fix: Lower the velocity threshold in config.py
FALL_VELOCITY_THRESHOLD = 10.0  # More sensitive (lower = easier to trigger)
# Press 'S' during execution to cycle sensitivity presets
```

---

## Need Help?

1. Check main README.md for detailed documentation
2. Review Troubleshooting section in README.md
3. Check ESP32 Serial Monitor (115200 baud) for error messages
4. Test connection: `ping YOUR_ESP32_IP`

---

**Total Setup Time: ~10 minutes** ✓
**Let's go! 🚀**
