/*
 * Buzzer Controller for Impact Alerts
 * 
 * Controls active or passive buzzer for impact detection
 */

#ifndef BUZZER_CONTROLLER_H
#define BUZZER_CONTROLLER_H

#include <Arduino.h>

// ============================================================================
// CONFIGURATION
// ============================================================================

// Buzzer type
#define ACTIVE_BUZZER     // Uncomment for active buzzer (has internal oscillator)
// #define PASSIVE_BUZZER // Uncomment for passive buzzer (needs PWM tone)

// Default buzzer patterns
#define IMPACT_BEEP_DURATION 500    // ms for each beep
#define IMPACT_BEEP_COUNT 6         // Number of beeps
#define IMPACT_BEEP_INTERVAL 95    // ms between beeps

#ifdef PASSIVE_BUZZER
#define BUZZER_FREQUENCY 2000       // Hz for passive buzzer
#endif

// ============================================================================
// BUZZER CONTROLLER CLASS
// ============================================================================

class BuzzerController {
private:
    int buzzerPin;
    unsigned long beepDuration;
    int beepCount;
    unsigned long beepInterval;
    
    #ifdef PASSIVE_BUZZER
    int buzzerFrequency;
    #endif
    
public:
    BuzzerController(int pin, 
                     unsigned long duration = IMPACT_BEEP_DURATION,
                     int count = IMPACT_BEEP_COUNT,
                     unsigned long interval = IMPACT_BEEP_INTERVAL) {
        buzzerPin = pin;
        beepDuration = duration;
        beepCount = count;
        beepInterval = interval;
        
        #ifdef PASSIVE_BUZZER
        buzzerFrequency = BUZZER_FREQUENCY;
        #endif
    }
    
    void begin() {
        pinMode(buzzerPin, OUTPUT);
        digitalWrite(buzzerPin, LOW);
        Serial.println("✓ Buzzer controller initialized");
    }
    
    // Single beep
    void beep() {
        #ifdef ACTIVE_BUZZER
        digitalWrite(buzzerPin, HIGH);
        delay(beepDuration);
        digitalWrite(buzzerPin, LOW);
        #endif
        
        #ifdef PASSIVE_BUZZER
        tone(buzzerPin, buzzerFrequency, beepDuration);
        delay(beepDuration);
        noTone(buzzerPin);
        #endif
    }
    
    // Multiple beeps (for impact alert)
    void impactAlert() {
        Serial.println("🔊 BUZZER: Impact alert pattern");
        
        for (int i = 0; i < beepCount; i++) {
            beep();
            
            // Pause between beeps (except after last beep)
            if (i < beepCount - 1) {
                delay(beepInterval);
            }
        }
    }
    
    // Continuous beep (for testing)
    void testBeep(unsigned long duration = 1000) {
        Serial.println("🔊 BUZZER: Test beep");
        
        #ifdef ACTIVE_BUZZER
        digitalWrite(buzzerPin, HIGH);
        delay(duration);
        digitalWrite(buzzerPin, LOW);
        #endif
        
        #ifdef PASSIVE_BUZZER
        tone(buzzerPin, buzzerFrequency, duration);
        delay(duration);
        noTone(buzzerPin);
        #endif
    }
    
    // Custom pattern: short-short-long (SOS-like)
    void warningPattern() {
        beep();
        delay(100);
        beep();
        delay(100);
        
        #ifdef ACTIVE_BUZZER
        digitalWrite(buzzerPin, HIGH);
        delay(500);
        digitalWrite(buzzerPin, LOW);
        #endif
        
        #ifdef PASSIVE_BUZZER
        tone(buzzerPin, buzzerFrequency, 500);
        delay(500);
        noTone(buzzerPin);
        #endif
    }
    
    // Configure beep pattern
    void setPattern(unsigned long duration, int count, unsigned long interval) {
        beepDuration = duration;
        beepCount = count;
        beepInterval = interval;
    }
    
    #ifdef PASSIVE_BUZZER
    void setFrequency(int frequency) {
        buzzerFrequency = frequency;
    }
    #endif
};

#endif // BUZZER_CONTROLLER_H
