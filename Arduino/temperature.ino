#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <Wire.h>

// SI7021 I2C address
#define si7021Addr 0x40

// Wi-Fi credentials
const char* SSID = "EE_GROUP_8";
const char* PASSWORD = "cyrusdavebading_123";
const char* SERVER_IP = "10.3.141.1";
const int SERVER_PORT = 8000;
const char* SENSOR_NAME = "TEMP_ONE";

// Delay between each temperature reading in milliseconds
unsigned long DELAY = 1000;

String SERVER_URL = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/esp82/temperature/";
String INIT_URL = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/esp82/initial/";

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

int initial_connection(){
    
    if (WiFi.status() != WL_CONNECTED){
        connectWiFi();
    }
    HTTPClient http;
    WiFiClient client;

    SerialLogging(2, "Sending initial connection request...");
    http.begin(client, INIT_URL);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    String post_data = "name=" + String(SENSOR_NAME) + "&battery_level=100&sensor_type=temperature";
    
    int http_response_code = http.POST(post_data);
    String response = http.getString();
    int size = 3;

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

void setup() {
    Serial.begin(9600);
    Wire.begin();
    WiFi.mode(WIFI_STA);
    connectWiFi();

    Wire.beginTransmission(si7021Addr);
    Wire.endTransmission();
    delay(300);
    int initData = 0;
    while (initData == 0){
        initData = initial_connection();
    }
    SerialLogging(1, "Initialization complete!");
}

void sendTemperature(float celsiusTemp) {
    if (WiFi.status() != WL_CONNECTED) {
        connectWiFi();  // Reconnect if disconnected
    }

    HTTPClient http;
    WiFiClient client;

    SerialLogging(2, "Sending temperature data to server...");
    http.begin(client, SERVER_URL);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    String postData = "temperature=" + String(celsiusTemp) + "&name=" + String(SENSOR_NAME) + "&battery_level=100";

    int httpResponseCode = http.POST(postData);
    if (httpResponseCode > 0) {
        String response = http.getString();
        int size = 3;

        String* parts = processResult(response, size);

        String status = parts[0];
        String message = parts[1];
        String delayTimeStr = parts[2];
        int delayTime = delayTimeStr.toInt();


        SerialLogging(4, "Temperature: " + String(celsiusTemp) + " C");
        SerialLogging(4, "Status: " + status);
        SerialLogging(4, "Message: " + message);
        SerialLogging(4, "Delay Time: " + delayTime);
        Serial.println();

        // Update the delay time if the response contains a valid delay time
        if (delayTime != DELAY) {
            SerialLogging(2, "Setting delay time to " + String(delayTime));
            DELAY = delayTime;
        }
    } else {
        SerialLogging(0, "Failed to send temperature data. HTTP Response Code: " + String(httpResponseCode));
    }

    http.end();
}

void loop() {
    unsigned int data[2];

    // Request humidity measurement
    Wire.beginTransmission(si7021Addr);
    Wire.write(0xF5);
    Wire.endTransmission();
    delay(500);

    // Read humidity data
    Wire.requestFrom(si7021Addr, 2);
    if (Wire.available() == 2) {
        data[0] = Wire.read();
        data[1] = Wire.read();
    }

    // Request temperature measurement
    Wire.beginTransmission(si7021Addr);
    Wire.write(0xF3);
    Wire.endTransmission();
    delay(500);

    // Read temperature data
    Wire.requestFrom(si7021Addr, 2);
    if (Wire.available() == 2) {
        data[0] = Wire.read();
        data[1] = Wire.read();
    }

    // Convert temperature data
    float temp = ((data[0] * 256.0) + data[1]);
    float celsiusTemp = ((175.72 * temp) / 65536.0) - 46.85;

    // Print to Serial
    SerialLogging(4, "Temperature: " + String(celsiusTemp) + " C");

    // Send the temperature data to the server
    sendTemperature(celsiusTemp);

    delay(DELAY); 
}
