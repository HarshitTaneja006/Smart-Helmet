# 👷 Smart Safety Helmet System

## Hybrid Motion & Impact Detection

---

# 🎯 Project Overview

**Goal:** Create a modular, production-ready safety helmet that detects accidents in real-time.

*   **Hybrid Detection:** Combines Motion Analysis (Background Subtraction) and Accelerometer Sensors.
*   **Edge Computing:** Heavy processing done on a local server/PC to save battery.
*   **Instant Alerts:** Audio (Buzzer) and Haptic (Vibration) feedback for the wearer.

---

# 🏗️ System Architecture

The system consists of two main parts communicating over WiFi:

1.  **The Helmet (Edge Device - ESP32-CAM)**
    *   Captures MJPEG video stream (640x480 @ ~10 FPS).
    *   Monitors impacts with MPU6050 accelerometer.
    *   Provides immediate local feedback (buzzer on impact).
2.  **The Server (Processing Unit - Python)**
    *   Analyzes video stream using MOG2 background subtraction.
    *   Tracks falling objects with centroid-based tracking.
    *   Compensates for helmet camera motion via optical flow.
    *   Sends alert commands back to helmet.

---

# 🧠 Feature 1: Visual Fall Detection

**How it works:**
*   **Camera:** ESP32-CAM streams MJPEG video to the server.
*   **Motion Detection:** Server uses **MOG2 background subtraction** to detect moving objects.
*   **Logic:**
    *   Detects ANY falling object (class-agnostic, no AI model needed).
    *   Tracks object centroids between frames.
    *   Measures vertical velocity (pixels per frame).
    *   Compensates for helmet camera motion using optical flow (Lucas-Kanade).
    *   Confirms fall based on velocity threshold and consecutive frames.

**Advantages:**
*   No object classification needed (detects any falling object).
*   Fast processing (< 50ms per frame).
*   Works in variable lighting conditions.
*   Minimal CPU/memory requirements.

---

# 💥 Feature 2: Physical Impact Detection

**How it works:**
*   **Sensor:** MPU6050 3-axis Accelerometer mounted on the helmet.
*   **Processing:** Runs directly on the ESP32 microcontroller (Offline capable).
*   **Trigger:**
    *   Continuously measures G-force on X, Y, Z axes.
    *   If total acceleration exceeds threshold (e.g., > 4.0G).
    *   **Action:** Instantly triggers the buzzer and vibration motor.

**Response Time:** < 50ms (no network latency).

---

# 🚨 Alert System

**Two-way Detection Loop:**

1.  **Server-Triggered (Visual Motion):**
    *   Server detects falling motion → Sends HTTP request to ESP32 → ESP32 activates vibration motor.
2.  **Local-Triggered (Physical Impact):**
    *   Accelerometer detects high G-force → ESP32 activates buzzer immediately (offline).

**Feedback Mechanisms:**
*   🔊 **Buzzer:** High-pitch audible alarm on impact (6 beeps pattern).
*   📳 **Vibration Motor:** Haptic feedback during fall detection.

---

# 🛠️ Tech Stack

**Hardware:**
*   ESP32-CAM Module (WiFi, Camera)
*   MPU6050 Accelerometer (3-axis motion sensing)
*   Active Buzzer / Vibration Motor (alerts)

**Software:**
*   **Firmware:** C++ (Arduino Framework)
*   **Backend:** Python 3.x
*   **Computer Vision:** OpenCV (MOG2, Lucas-Kanade Optical Flow)
*   **Communication:** HTTP / REST API over WiFi

---

# 🚀 Future Improvements

*   **GPS Integration:** Send location coordinates via SMS/GSM module upon accident.
*   **Cloud Dashboard:** Log incidents to a web dashboard for safety managers.
*   **Advanced Pose Tracking:** Optional skeletal tracking for enhanced accuracy.
*   **Multi-camera Support:** Monitor from multiple angles.

---

# ❓ Q&A

**Thank you!**
