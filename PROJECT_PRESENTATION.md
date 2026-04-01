# 👷 Smart Safety Helmet System
## AI-Powered Fall & Impact Detection

---

# 🎯 Project Overview

**Goal:** Create a modular, production-ready safety helmet that detects accidents in real-time.

*   **Hybrid Detection:** Combines Computer Vision (AI) and Physical Sensors.
*   **Edge Computing:** Heavy processing done on a local server/PC to save battery.
*   **Instant Alerts:** Audio (Buzzer) and Haptic (Vibration) feedback for the wearer.

---

# 🏗️ System Architecture

The system consists of two main parts communicating over WiFi:

1.  **The Helmet (Edge Device - ESP32-CAM)**
    *   Captures live video stream.
    *   Monitors physical forces (G-force).
    *   Provides immediate local feedback.
2.  **The Server (Processing Unit - Python)**
    *   Analyzes video stream using Deep Learning.
    *   Tracks objects and detects abnormal movements.
    *   Sends alert commands back to the helmet.

---

# 🧠 Feature 1: Visual Fall Detection

**How it works:**
*   **Camera:** ESP32-CAM streams video to the server.
*   **AI Model:** Server runs **YOLOv5** (You Only Look Once) to detect people.
*   **Logic:**
    *   Tracks the "Person" class.
    *   Analyzes bounding box aspect ratio (width vs. height).
    *   Detects rapid changes in posture indicating a fall.

---

# 💥 Feature 2: Physical Impact Detection

**How it works:**
*   **Sensor:** MPU6050 / ADXL345 Accelerometer mounted on the helmet.
*   **Processing:** Runs directly on the ESP32 microcontroller (Offline capable).
*   **Trigger:**
    *   Continuously measures G-force on X, Y, Z axes.
    *   If total acceleration exceeds a safety threshold (e.g., > 2.5G).
    *   **Action:** Instantly triggers the buzzer and vibration motor.

---

# 🚨 Alert System

**Two-way Communication Loop:**

1.  **Server-Triggered (Visual):**
    *   Server detects fall -> Sends HTTP request to ESP32 -> ESP32 activates buzzer.
2.  **Local-Triggered (Physical):**
    *   Accelerometer detects impact -> ESP32 activates buzzer immediately (0 latency).

**Feedback Mechanisms:**
*   🔊 **Buzzer:** High-pitch audible alarm.
*   📳 **Vibration Motor:** Haptic feedback against the helmet shell.

---

# 🛠️ Tech Stack

**Hardware:**
*   ESP32-CAM Module
*   MPU6050 Accelerometer
*   Active Buzzer / Vibration Motor

**Software:**
*   **Firmware:** C++ (Arduino Framework)
*   **Backend:** Python 3.x
*   **AI/ML:** PyTorch, YOLOv5, ONNX Runtime
*   **Communication:** HTTP / REST API over WiFi

---

# 🚀 Future Improvements

*   **GPS Integration:** Send location coordinates via SMS/GSM module upon accident.
*   **Cloud Dashboard:** Log incidents to a web dashboard for safety managers.
*   **Pose Estimation:** Upgrade from bounding boxes to skeletal tracking for higher accuracy.

---

# ❓ Q&A

**Thank you!**
