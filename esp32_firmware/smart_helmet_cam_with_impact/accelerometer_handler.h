/*
 * GY-521 (MPU6050) Accelerometer Handler
 *
 * Detects sudden impacts using the MPU6050 3-axis accelerometer
 * on the GY-521 breakout board via I2C.
 *
 * Wiring (ESP32-CAM AI-Thinker):
 *   GY-521 VCC  -> 3.3V
 *   GY-521 GND  -> GND
 *   GY-521 SDA  -> GPIO 14
 *   GY-521 SCL  -> GPIO 15
 *   GY-521 AD0  -> GND (address 0x68)
 */

#ifndef ACCELEROMETER_HANDLER_H
#define ACCELEROMETER_HANDLER_H

#include <Wire.h>

// I2C Pins for ESP32-CAM
#define I2C_SDA 14
#define I2C_SCL 15

// MPU6050 I2C address (0x68 when AD0=GND, 0x69 when AD0=VCC)
#define MPU6050_ADDR 0x68

// MPU6050 Registers
#define MPU6050_PWR_MGMT_1    0x6B
#define MPU6050_ACCEL_XOUT_H  0x3B
#define MPU6050_ACCEL_CONFIG  0x1C
#define MPU6050_CONFIG        0x1A
#define MPU6050_WHO_AM_I      0x75

// Impact detection defaults
#define IMPACT_THRESHOLD_G  4.0   // g-force threshold
#define IMPACT_DEBOUNCE_MS  500   // prevent repeated triggers

class AccelerometerHandler {
private:
    unsigned long lastImpactTime;
    float impactThreshold;
    bool initialized;

    int16_t read16(uint8_t reg) {
        Wire.beginTransmission(MPU6050_ADDR);
        Wire.write(reg);
        Wire.endTransmission(false);
        Wire.requestFrom(MPU6050_ADDR, (uint8_t)2);
        int16_t value = Wire.read() << 8;
        value |= Wire.read();
        return value;
    }

    void writeRegister(uint8_t reg, uint8_t value) {
        Wire.beginTransmission(MPU6050_ADDR);
        Wire.write(reg);
        Wire.write(value);
        Wire.endTransmission();
    }

public:
    AccelerometerHandler(float threshold = IMPACT_THRESHOLD_G) {
        impactThreshold = threshold;
        lastImpactTime = 0;
        initialized = false;
    }

    bool begin() {
        Wire.begin(I2C_SDA, I2C_SCL);
        delay(100);

        Serial.println("Initializing GY-521 (MPU6050)...");

        // Check WHO_AM_I register (should return 0x68)
        Wire.beginTransmission(MPU6050_ADDR);
        if (Wire.endTransmission() != 0) {
            Serial.println("✗ GY-521 not found - check wiring:");
            Serial.println("    SDA -> GPIO 14");
            Serial.println("    SCL -> GPIO 15");
            Serial.println("    AD0 -> GND");
            return false;
        }

        // Wake up MPU6050 (clear sleep bit)
        writeRegister(MPU6050_PWR_MGMT_1, 0x00);
        delay(100);

        // Set accelerometer range to ±8g
        // 0x00=±2g, 0x08=±4g, 0x10=±8g, 0x18=±16g
        writeRegister(MPU6050_ACCEL_CONFIG, 0x10);
        delay(10);

        // Set DLPF to ~20Hz bandwidth to filter vibration noise
        // 0x04 = Accel BW 21Hz, Gyro BW 20Hz
        writeRegister(MPU6050_CONFIG, 0x04);
        delay(10);

        Serial.println("✓ GY-521 (MPU6050) initialized (±8g, DLPF 20Hz)");
        initialized = true;
        return true;
    }

    bool checkImpact() {
        if (!initialized) return false;

        int16_t rawX = read16(MPU6050_ACCEL_XOUT_H);
        int16_t rawY = read16(MPU6050_ACCEL_XOUT_H + 2);
        int16_t rawZ = read16(MPU6050_ACCEL_XOUT_H + 4);

        // Convert to g (±8g range = 4096 LSB/g)
        float ax = rawX / 4096.0;
        float ay = rawY / 4096.0;
        float az = rawZ / 4096.0;

        // Total acceleration magnitude minus gravity
        float totalAccel = sqrt(ax * ax + ay * ay + az * az);
        float impactForce = abs(totalAccel - 1.0);

        if (impactForce > impactThreshold) {
            unsigned long currentTime = millis();
            if ((currentTime - lastImpactTime) > IMPACT_DEBOUNCE_MS) {
                lastImpactTime = currentTime;

                Serial.print("🔨 IMPACT DETECTED! Force: ");
                Serial.print(impactForce);
                Serial.println("g");

                return true;
            }
        }

        return false;
    }

    void setThreshold(float threshold) {
        impactThreshold = threshold;
        Serial.print("Impact threshold set to: ");
        Serial.print(threshold);
        Serial.println("g");
    }

    bool isInitialized() {
        return initialized;
    }
};

#endif // ACCELEROMETER_HANDLER_H
