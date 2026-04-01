/*
 * Smart Safety Helmet - ESP32-CAM Firmware with Impact Detection
 * 
 * Hardware:
 * - ESP32-CAM (AI-Thinker)
 * - OV2640 Camera Module
 * - Vibration Motor on GPIO 12 (for fall detection)
 * - Buzzer on GPIO 13 (for impact detection)
 * - GY-521 (MPU6050) Accelerometer on I2C (GPIO 14=SDA, 15=SCL)
 *
 * Endpoints (port 80):
 * - GET /capture       - Returns single JPEG image
 * - GET /vibrate       - Triggers vibration motor (fall alert)
 * - GET /impact        - Triggers buzzer (impact alert - for testing)
 * - GET /status        - System status
 *
 * Streaming (port 81):
 * - GET /stream        - MJPEG video stream (used by edge server)
 */

#include "esp_camera.h"
#include "esp_http_server.h"
#include "WiFi.h"
#include "camera_handler.h"
#include "motor_controller.h"
#include "buzzer_controller.h"
#include "accelerometer_handler.h"

// ============================================================================
// CONFIGURATION - EDIT THESE
// ============================================================================

// WiFi credentials
const char* WIFI_SSID = "Harshit";
const char* WIFI_PASSWORD = "987654321";

// Pin definitions
#define MOTOR_PIN 12    // Vibration motor (fall detection)
#define BUZZER_PIN 13   // Buzzer (impact detection)

// Impact detection settings
#define IMPACT_CHECK_INTERVAL 50  // Check every 50ms (20 Hz)
#define ENABLE_IMPACT_DETECTION true  // Set to false to disable

// ============================================================================
// GLOBAL VARIABLES
// ============================================================================

httpd_handle_t camera_httpd = NULL;
httpd_handle_t stream_httpd = NULL;
MotorController motor(MOTOR_PIN);
BuzzerController buzzer(BUZZER_PIN);
AccelerometerHandler accel(4.0);  // 4g threshold

unsigned long lastImpactCheck = 0;
unsigned long impactCount = 0;

// ============================================================================
// HTTP HANDLERS
// ============================================================================

// Capture endpoint - returns JPEG image
static esp_err_t capture_handler(httpd_req_t *req) {
    camera_fb_t *fb = esp_camera_fb_get();
    
    if (!fb) {
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }
    
    httpd_resp_set_type(req, "image/jpeg");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    
    esp_err_t res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
    
    esp_camera_fb_return(fb);
    return res;
}

// Vibrate endpoint - triggers motor (fall alert from camera)
static esp_err_t vibrate_handler(httpd_req_t *req) {
    motor.trigger();
    
    httpd_resp_set_type(req, "text/plain");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_send(req, "OK", 2);
    
    return ESP_OK;
}

// Impact endpoint - triggers buzzer (for testing)
static esp_err_t impact_handler(httpd_req_t *req) {
    buzzer.impactAlert();
    
    httpd_resp_set_type(req, "text/plain");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_send(req, "OK", 2);
    
    return ESP_OK;
}

// Status endpoint - system info
static esp_err_t status_handler(httpd_req_t *req) {
    char response[300];
    snprintf(response, sizeof(response),
             "{\n"
             "  \"status\": \"online\",\n"
             "  \"uptime\": %lu,\n"
             "  \"free_heap\": %u,\n"
             "  \"camera\": \"ready\",\n"
             "  \"accelerometer\": \"%s\",\n"
             "  \"impact_count\": %lu\n"
             "}",
             millis() / 1000,
             ESP.getFreeHeap(),
             accel.isInitialized() ? "ready" : "not found",
             impactCount);
    
    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_send(req, response, strlen(response));
    
    return ESP_OK;
}

// ============================================================================
// MJPEG STREAM HANDLER (port 81)
// ============================================================================

#define PART_BOUNDARY "123456789000000000000987654321"
static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* _STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

static esp_err_t stream_handler(httpd_req_t *req) {
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    char part_buf[64];

    res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
    if (res != ESP_OK) return res;
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

    Serial.println("Stream client connected");

    while (true) {
        fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("Stream: frame capture failed");
            res = ESP_FAIL;
            break;
        }

        size_t hlen = snprintf(part_buf, 64, _STREAM_PART, fb->len);
        res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
        if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, part_buf, hlen);
        }
        if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
        }

        esp_camera_fb_return(fb);

        if (res != ESP_OK) break;
    }

    Serial.println("Stream client disconnected");
    return res;
}

// ============================================================================
// HTTP SERVER SETUP
// ============================================================================

void startCameraServer() {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 80;
    
    // URI handlers
    httpd_uri_t capture_uri = {
        .uri       = "/capture",
        .method    = HTTP_GET,
        .handler   = capture_handler,
        .user_ctx  = NULL
    };
    
    httpd_uri_t vibrate_uri = {
        .uri       = "/vibrate",
        .method    = HTTP_GET,
        .handler   = vibrate_handler,
        .user_ctx  = NULL
    };
    
    httpd_uri_t impact_uri = {
        .uri       = "/impact",
        .method    = HTTP_GET,
        .handler   = impact_handler,
        .user_ctx  = NULL
    };
    
    httpd_uri_t status_uri = {
        .uri       = "/status",
        .method    = HTTP_GET,
        .handler   = status_handler,
        .user_ctx  = NULL
    };
    
    if (httpd_start(&camera_httpd, &config) == ESP_OK) {
        httpd_register_uri_handler(camera_httpd, &capture_uri);
        httpd_register_uri_handler(camera_httpd, &vibrate_uri);
        httpd_register_uri_handler(camera_httpd, &impact_uri);
        httpd_register_uri_handler(camera_httpd, &status_uri);

        Serial.println("HTTP server started on port 80");
    }

    // Start MJPEG stream server on port 81
    httpd_uri_t stream_uri = {
        .uri       = "/stream",
        .method    = HTTP_GET,
        .handler   = stream_handler,
        .user_ctx  = NULL
    };

    config.server_port = 81;
    config.ctrl_port = config.ctrl_port + 1;

    if (httpd_start(&stream_httpd, &config) == ESP_OK) {
        httpd_register_uri_handler(stream_httpd, &stream_uri);
        Serial.println("Stream server started on port 81");
    }
}

// ============================================================================
// SETUP
// ============================================================================

void setup() {
    Serial.begin(115200);
    Serial.println("\n\n===========================================");
    Serial.println("Smart Safety Helmet - ESP32-CAM");
    Serial.println("With Impact Detection");
    Serial.println("===========================================\n");
    
    // Initialize motor
    motor.begin();
    
    // Initialize buzzer
    buzzer.begin();
    
    // Initialize accelerometer
    if (ENABLE_IMPACT_DETECTION) {
        Serial.println("Initializing impact detection...");
        if (accel.begin()) {
            Serial.println("✓ Impact detection enabled");
        } else {
            Serial.println("⚠️  Accelerometer not found - impact detection disabled");
            Serial.println("   System will continue with fall detection only");
        }
    } else {
        Serial.println("⚠️  Impact detection disabled in config");
    }
    
    // Initialize camera
    if (!initCamera()) {
        Serial.println("Camera init FAILED!");
        while(1) {
            delay(1000);
        }
    }
    Serial.println("✓ Camera initialized");
    
    // Connect to WiFi
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.print("Connecting to WiFi");
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    Serial.println("\n✓ WiFi connected");
    Serial.println("\n===========================================");
    Serial.println("COPY THIS IP ADDRESS:");
    Serial.print(">>> ");
    Serial.print(WiFi.localIP());
    Serial.println(" <<<");
    Serial.println("===========================================\n");
    
    Serial.println("Available endpoints:");
    Serial.print("  http://");
    Serial.print(WiFi.localIP());
    Serial.println("/capture  - Get camera image");
    Serial.print("  http://");
    Serial.print(WiFi.localIP());
    Serial.println("/vibrate  - Trigger vibration motor (fall alert)");
    Serial.print("  http://");
    Serial.print(WiFi.localIP());
    Serial.println("/impact   - Trigger buzzer (impact alert - test)");
    Serial.print("  http://");
    Serial.print(WiFi.localIP());
    Serial.println("/status   - System status");
    Serial.print("  http://");
    Serial.print(WiFi.localIP());
    Serial.println(":81/stream - MJPEG video stream");
    
    // Start HTTP server
    startCameraServer();
    
    Serial.println("\n✓ System ready!");
    
    // Test devices
    Serial.println("\nTesting devices...");
    
    Serial.println("Testing vibration motor...");
    motor.trigger();
    delay(600);
    
    Serial.println("Testing buzzer...");
    buzzer.testBeep(300);
    
    Serial.println("\n===========================================");
    Serial.println("Monitoring for impacts...");
    Serial.println("===========================================\n");
}

// ============================================================================
// LOOP
// ============================================================================

void loop() {
    // Check for impacts at regular intervals
    if (ENABLE_IMPACT_DETECTION && accel.isInitialized()) {
        unsigned long currentTime = millis();
        
        if ((currentTime - lastImpactCheck) >= IMPACT_CHECK_INTERVAL) {
            lastImpactCheck = currentTime;
            
            // Check for impact
            if (accel.checkImpact()) {
                impactCount++;
                
                // Trigger buzzer alert
                buzzer.impactAlert();
                
                Serial.print("Total impacts detected: ");
                Serial.println(impactCount);
            }
        }
    }
    
    // Small delay to prevent watchdog issues
    delay(1);
}
