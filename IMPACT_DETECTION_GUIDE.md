# 🔨 IMPACT DETECTION - Setup Guide

## 🎯 What You're Adding

**Impact Detection System:**
- Detects when helmet is physically hit
- Triggers buzzer immediately
- Independent from camera-based fall detection
- Works offline (no WiFi needed)

---

## 🛠️ Hardware Requirements

### Required Components:

1. **Accelerometer** (choose ONE):
   - ✅ **MPU6050** (recommended) - $2-3
     - 3-axis accelerometer + gyroscope
     - I2C interface
     - Common, well-supported
   
   - ✅ **ADXL345** (alternative) - $3-5
     - 3-axis accelerometer
     - I2C interface
     - Slightly more accurate

2. **Buzzer** (you have this):
   - ✅ **Active Buzzer** (recommended) - has internal oscillator
     - Just apply voltage, it beeps
     - Easier to use
   
   - ✅ **Passive Buzzer** (alternative) - needs PWM signal
     - Can change tone/frequency
     - More flexible

3. **Wiring Supplies**:
   - Jumper wires (male-female)
   - Breadboard (optional, for testing)
   - Soldering kit (for permanent installation)

---

## 🔌 Wiring Diagram

### Complete System Connections:

```
ESP32-CAM Pinout:
┌─────────────────────────────────────┐
│                                     │
│  [ESP32-CAM Module]                │
│                                     │
│  GPIO 12 ──────> Vibration Motor   │  Fall Detection (camera-based)
│  GPIO 13 ──────> Buzzer            │  Impact Detection (accelerometer)
│  GPIO 14 ──────> Accelerometer SDA │  I2C Data
│  GPIO 15 ──────> Accelerometer SCL │  I2C Clock
│  GND     ──────> Common Ground     │
│  3.3V    ──────> Accelerometer VCC │
│  5V      ──────> Motors/Buzzer VCC │
│                                     │
└─────────────────────────────────────┘
```

---

## 📐 Detailed Connections

### 1. MPU6050 Accelerometer → ESP32-CAM

```
MPU6050          ESP32-CAM
────────         ─────────
VCC    ────────> 3.3V
GND    ────────> GND
SDA    ────────> GPIO 14
SCL    ────────> GPIO 15
```

**⚠️ IMPORTANT:**
- MPU6050 uses **3.3V**, NOT 5V!
- Double-check SDA/SCL connections
- Use short wires (<10cm) for stable I2C

---

### 2. Buzzer → ESP32-CAM

#### Option A: Active Buzzer (Recommended)
```
Active Buzzer    ESP32-CAM
─────────────    ─────────
(+) Positive  ──> GPIO 13
(-) Negative  ──> GND

OR with transistor (if buzzer needs >20mA):

GPIO 13 ──[ 1kΩ ]──> NPN Base (2N2222)
                     Emitter ──> GND
                     Collector ──> Buzzer (-)
Buzzer (+) ──────────────────> 5V
```

#### Option B: Passive Buzzer
```
Passive Buzzer   ESP32-CAM
──────────────   ─────────
(+) Positive  ──> GPIO 13
(-) Negative  ──> GND
```

---

### 3. Vibration Motor (Existing)

```
Vibration Motor  ESP32-CAM
───────────────  ─────────
(+) Red Wire  ──> GPIO 12 (via transistor)
(-) Black Wire──> GND
```

---

## 🔧 Assembly Steps

### Step 1: Prepare Components

1. **Identify your buzzer type:**
   ```
   Active Buzzer:  Has sticker on bottom, internal circuit visible
   Passive Buzzer: No sticker, just a piezo element
   ```

2. **Check accelerometer pins:**
   - MPU6050 has 8 pins (VCC, GND, SDA, SCL, + extras)
   - Only need 4 pins: VCC, GND, SDA, SCL

---

### Step 2: Connect Accelerometer

1. **MPU6050 to ESP32-CAM:**
   ```
   Red wire    (VCC) ──> 3.3V
   Black wire  (GND) ──> GND
   Green wire  (SDA) ──> GPIO 14
   Yellow wire (SCL) ──> GPIO 15
   ```

2. **Secure connections:**
   - For testing: Use breadboard
   - For permanent: Solder connections

---

### Step 3: Connect Buzzer

1. **Identify polarity:**
   - Active buzzer: Long leg = (+), short leg = (-)
   - Passive buzzer: Usually marked with (+) symbol

2. **Connect to ESP32:**
   ```
   Buzzer (+) ──> GPIO 13
   Buzzer (-) ──> GND
   ```

3. **If buzzer is loud and needs transistor:**
   ```
   GPIO 13 ──[ 1kΩ resistor ]──> 2N2222 Base
   2N2222 Emitter ──> GND
   2N2222 Collector ──> Buzzer (-)
   Buzzer (+) ──> 5V
   ```

---

## 💻 Software Setup

### Step 1: Edit Buzzer Type

Open `buzzer_controller.h` and choose your buzzer type:

```cpp
// Line 13-14: Choose ONE
#define ACTIVE_BUZZER     // ✓ For active buzzer
// #define PASSIVE_BUZZER // ✓ For passive buzzer
```

---

### Step 2: Edit Accelerometer Type

Open `accelerometer_handler.h` and choose your sensor:

```cpp
// Line 13-14: Choose ONE
#define USE_MPU6050      // ✓ For MPU6050
// #define USE_ADXL345   // ✓ For ADXL345
```

---

### Step 3: Adjust Impact Sensitivity (Optional)

In `accelerometer_handler.h`:

```cpp
// Line 22: Impact threshold
#define IMPACT_THRESHOLD_G 4.0

// Sensitivity guide:
// 2.0 = Very sensitive (detects light taps)
// 4.0 = Moderate (default, good for construction)
// 8.0 = Less sensitive (only hard impacts)
```

---

### Step 4: Upload Firmware

1. **Open in Arduino IDE:**
   - `smart_helmet_cam_with_impact.ino`

2. **Edit WiFi credentials (lines 25-26):**
   ```cpp
   const char* WIFI_SSID = "Your_WiFi_Name";
   const char* WIFI_PASSWORD = "Your_Password";
   ```

3. **Upload to ESP32-CAM**

4. **Open Serial Monitor (115200 baud)**

---

## ✅ Testing

### Test 1: Accelerometer Detection

**Serial Monitor should show:**
```
Initializing impact detection...
Initializing MPU6050...
✓ MPU6050 initialized
✓ Impact detection enabled
```

**If you see:**
```
✗ MPU6050 not found
```
**Fix:**
- Check wiring (SDA/SCL swapped?)
- Verify 3.3V power
- Try different I2C address (some modules use 0x69 instead of 0x68)

---

### Test 2: Buzzer Sound

**What happens:**
- At startup, buzzer plays test beep (300ms)

**If no sound:**
- Check buzzer polarity (+/-)
- Verify GPIO 13 connection
- Check if active/passive setting matches your buzzer
- Test with endpoint: `http://ESP32_IP/impact`

---

### Test 3: Impact Detection

1. **Tap the helmet/module gently**
2. **Serial Monitor shows:**
   ```
   🔨 IMPACT DETECTED! Force: 4.2g
   🔊 BUZZER: Impact alert pattern
   Total impacts detected: 1
   ```

3. **Buzzer plays:** 3 short beeps (beep-beep-beep)

**If no detection:**
- Lower threshold in `accelerometer_handler.h`
- Tap harder
- Check accelerometer is firmly mounted

---

## 🎵 Alert Patterns

### Fall Detection (Camera):
- **Vibration motor**: 500ms continuous
- **Laptop beep**: Single 300ms tone
- **Laptop screen**: Red alert for 2 seconds

### Impact Detection (Accelerometer):
- **Buzzer**: 3 short beeps (200ms each)
- **Pattern**: beep-pause-beep-pause-beep
- **Independent**: Works even if WiFi is down

---

## ⚙️ Customization

### Change Buzzer Pattern

Edit `smart_helmet_cam_with_impact.ino` line 23:

```cpp
// Current: 3 beeps, 200ms each, 100ms between
BuzzerController buzzer(BUZZER_PIN, 200, 3, 100);

// Make it longer:
BuzzerController buzzer(BUZZER_PIN, 300, 5, 150);
//                                    ^^^  ^  ^^^
//                                    ms   #  gap
```

### Change Impact Sensitivity

Edit `smart_helmet_cam_with_impact.ino` line 22:

```cpp
AccelerometerHandler accel(4.0);  // Current: 4g threshold

// More sensitive (detects lighter taps):
AccelerometerHandler accel(2.0);

// Less sensitive (only hard hits):
AccelerometerHandler accel(8.0);
```

---

## 🐛 Troubleshooting

### "Accelerometer not found"
```
Fix 1: Check wiring
  - SDA to GPIO 14
  - SCL to GPIO 15
  - VCC to 3.3V (NOT 5V!)
  - GND to GND

Fix 2: Check I2C address
  - Some MPU6050 use 0x69 instead of 0x68
  - Edit accelerometer_handler.h line 29:
    #define MPU6050_ADDR 0x69
```

### "Buzzer not beeping"
```
Fix 1: Check polarity
  - Swap (+) and (-) connections

Fix 2: Check buzzer type
  - Verify ACTIVE_BUZZER or PASSIVE_BUZZER setting
  - Try the opposite setting

Fix 3: Test manually
  - Visit: http://ESP32_IP/impact
  - Should trigger buzzer
```

### "Too many false alarms"
```
Fix: Increase threshold
  - Edit accelerometer_handler.h line 22
  - Change to: #define IMPACT_THRESHOLD_G 6.0
  - Or higher (up to 16.0)
```

### "Missed impacts"
```
Fix: Decrease threshold
  - Edit accelerometer_handler.h line 22
  - Change to: #define IMPACT_THRESHOLD_G 2.0
  - Or test by tapping harder
```

---

## 📊 Complete System Summary

| Detection Type | Sensor | Alert Device | Location | Speed |
|----------------|--------|--------------|----------|-------|
| **Fall Detection** | Camera (OV2640) | Vibration Motor | Helmet | ~200ms |
| **Fall Detection** | Camera (OV2640) | Laptop Beep | Laptop | ~200ms |
| **Impact Detection** | MPU6050 | Buzzer | Helmet | <50ms |

**You now have DUAL PROTECTION:**
- Camera detects falling objects BEFORE they hit
- Accelerometer detects impact WHEN it happens

---

## 📦 Parts List with Links

| Part | Quantity | Price | Notes |
|------|----------|-------|-------|
| ESP32-CAM | 1 | $8-10 | Already have |
| MPU6050 | 1 | $2-3 | Order from Amazon/AliExpress |
| Active Buzzer | 1 | $1-2 | Already have |
| Vibration Motor | 1 | $1-2 | Already have |
| Jumper Wires | 10 | $2-3 | F-F or M-F |
| **TOTAL** | - | **~$2-5** | Just need accelerometer! |

---

**Ready to wire it up! Let me know if you need help with any step.** 🚀
