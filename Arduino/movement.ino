#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* SSID = "EE_GROUP_8";
const char* PASSWORD = "cyrusdavebading_123";
const char* SERVER_IP = "10.3.141.1";
const int SERVER_PORT = 8000;
const char* SENSOR_NAME = "PIR_ONE";

const String INIT_URL = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/esp82/initial/";
const String SERVER_URL = String("http://") + SERVER_IP + ":" + String(SERVER_PORT) + "/api/esp82/motion/";
const int SENSOR_PIN = 13;  // Digital pin D7

unsigned long DELAY = 1000;

void SerialLogging(int status, String message){
    if (status == 0){
        Serial.println("[ERROR] " + message);
    } else if (status == 1){
        Serial.println("[SUCCESS] " + message);
    } else if (status == 2){
        Serial.println("[INFO] " + message);
    } else {
        Serial.println("[MESSAGE] " + message);
    }
}


String* processResult(String input, int &size) {
    const int MAX_PARTS = 3;
    static String parts[MAX_PARTS]; 
    size = 0;

    int start = 0;
    int end = input.indexOf('|');  

    while (end != -1 && size < MAX_PARTS) {
        parts[size++] = input.substring(start, end);
        start = end + 1;
        end = input.indexOf('|', start); 
    }

    if (size < MAX_PARTS) {
        parts[size++] = input.substring(start);
    }

    return parts; 
}

int initial_connection(){
    
    if (WiFi.status() != WL_CONNECTED){
        connectWiFi();
    }
    HTTPClient http;
    WiFiClient client;

    SerialLogging(2, "Initializing connection to server...");
    http.begin(client, INIT_URL);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    String post_data = "name=" + String(SENSOR_NAME) + "&battery_level=100&sensor_type=motion";
    
    int http_response_code = http.POST(post_data);
    
    int size = 3;
    String response = http.getString();

    String* parts = processResult(response, size);
    int delayTime = parts[2].toInt();
    
    if (delayTime > 0){
        SerialLogging(2, "Setting delay time to " + String(delayTime));
        DELAY = delayTime;
    }

    http.end();

    if (http_response_code > 0){
        return 1;
    } else {
        return 0;
    }
    

}

void connectWiFi() {
    SerialLogging(2, "Connecting to WiFi...");
    
    WiFi.begin(SSID, PASSWORD);

    int retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 20) {
        delay(1000);
        Serial.print(".");
        retries++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        SerialLogging(1, "Connected to WiFi!");
        SerialLogging(1, "IP Address: " + WiFi.localIP().toString());
    } else {
        SerialLogging(0, "Failed to connect to WiFi. Restarting...");
        ESP.restart();
    }
}

void setup() {
    Serial.begin(9600);
    
    pinMode(SENSOR_PIN, INPUT);
  
    WiFi.mode(WIFI_STA);
    connectWiFi();

    delay(300);
    int initData = 0;
    while (initData == 0){
        initData = initial_connection();
    }
    SerialLogging(2, "Finished initializing..");
}


void loop() {
    static unsigned long lastMotionTime = millis();
    long state = digitalRead(SENSOR_PIN);

    if (WiFi.status() != WL_CONNECTED) {
        connectWiFi(); 
    }

    if (state != HIGH) {
        SerialLogging(4, "Motion: Not Detected");
        if (millis() - lastMotionTime >= 300000) { // 5 minutes = 300000 ms
            SerialLogging(4, "No motion for 5 minutes. Sending no motion data...");
            WiFiClient client;
            HTTPClient http;

            http.begin(client, SERVER_URL);
            http.addHeader("Content-Type", "application/x-www-form-urlencoded");
            String postData = String("motion=false") + "&name=" + SENSOR_NAME + "&battery_level=100";

            int httpResponseCode = http.POST(postData);
            if (httpResponseCode > 0) {
                String response = http.getString();

                int size = 3;
                String* parts = processResult(response, size);
                int delayTime = parts[2].toInt();

                SerialLogging(4, "Status: " + parts[0]);
                SerialLogging(4, "Message: " + parts[1]);
                SerialLogging(4, "Delay Time: " + parts[2]);
                Serial.println();

                if (delayTime != DELAY) {
                    DELAY = delayTime;
                    SerialLogging(2, "Setting delay time to " + String(DELAY));
                }
            } else {
                SerialLogging(0, "Error: " + http.errorToString(httpResponseCode));
            }

            http.end();
            lastMotionTime = millis(); // Reset the timer after sending data
        }
        delay(DELAY);
        return;
    }

    SerialLogging(4, "Motion: Detected");
    lastMotionTime = millis(); // Update the last motion time
    WiFiClient client;
    HTTPClient http;

    http.begin(client, SERVER_URL);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    String postData = String("motion=true") + "&name=" + SENSOR_NAME + "&battery_level=100";

    int httpResponseCode = http.POST(postData);
    delay(60000);
    if (httpResponseCode > 0) {
        String response = http.getString();

        int size = 3;
        String* parts = processResult(response, size);
        int delayTime = parts[2].toInt();

        SerialLogging(4, "Status: " + parts[0]);
        SerialLogging(4, "Message: " + parts[1]);
        SerialLogging(4, "Delay Time: " + parts[2]);
        Serial.println();

        if (delayTime != DELAY) {
            DELAY = delayTime;
            SerialLogging(2, "Setting delay time to " + String(DELAY));
        }
    } else {
        SerialLogging(0, "Error: " + http.errorToString(httpResponseCode));
    }

    http.end();
    delay(DELAY);
}
