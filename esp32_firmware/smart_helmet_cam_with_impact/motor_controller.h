/*
 * Motor Controller for Vibration Motor
 * 
 * Controls vibration motor for fall alerts
 */

#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H

#include <Arduino.h>

class MotorController {
private:
    int motorPin;
    unsigned long vibrationDuration;
    
public:
    MotorController(int pin, unsigned long duration = 500) {
        motorPin = pin;
        vibrationDuration = duration;
    }
    
    void begin() {
        pinMode(motorPin, OUTPUT);
        digitalWrite(motorPin, LOW);
        Serial.println("✓ Motor controller initialized");
    }
    
    void trigger() {
        digitalWrite(motorPin, HIGH);
        Serial.println("🔔 MOTOR ACTIVATED");
        delay(vibrationDuration);
        digitalWrite(motorPin, LOW);
    }
    
    void setDuration(unsigned long duration) {
        vibrationDuration = duration;
    }
};

#endif // MOTOR_CONTROLLER_H
