/*  For Normally Closed:
    LOW = ON
    HIGH = OFF
    
    For Normally Open:
    LOW = OFF 
    HIGH = ON

Relay     NodeMCU
  +   ->    3V
  -   ->    G
  S   ->    D2
*/

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#define relay_pin 4

const char* SSID = "EE_GROUP_8";
const char* PASSWORD = "cyrusdavebading_123";
const char* SERVER_IP = "10.3.141.1";
const int SERVER_PORT = 8000;
const char* SENSOR_NAME = "LED_ONE";

const String INIT_URL = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/esp82/initial/";
const String SERVER_URL = String("http://") + SERVER_IP + ":" + String(SERVER_PORT) + "/api/esp82/led/";
unsigned long DELAY = 1000;

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

int initial_connection(){
    
    if (WiFi.status() != WL_CONNECTED){
        connectWiFi();
    }
    HTTPClient http;
    WiFiClient client;

    SerialLogging(2, "Initializing connection to server...");
    http.begin(client, INIT_URL);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    String post_data = "name=" + String(SENSOR_NAME) + "&battery_level=100&sensor_type=led";
    
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


void setup() {
    Serial.begin(9600);
    connectWiFi();
    pinMode(relay_pin, OUTPUT);

    delay(300);
    int initData = 0;
    while (initData == 0){
        initData = initial_connection();
    }
    SerialLogging(2, "Finished initializing..");

}
void loop() {
    if (WiFi.status() != WL_CONNECTED) {
        connectWiFi(); 
    }

    WiFiClient client;
    HTTPClient http;

    http.begin(client, SERVER_URL);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    String postData = "name=" + String(SENSOR_NAME) + "&battery_level=100";

    int httpResponseCode = http.POST(postData);

    if (httpResponseCode > 0){
        String response = http.getString();

        int size = 3;
        String* parts = processResult(response, size);
        int delayTime = parts[2].toInt();

        SerialLogging(4, "Status: " + parts[0]);
        SerialLogging(4, "Message: " + parts[1]);
        SerialLogging(4, "Delay Time: " + parts[2]);
        Serial.println();

        if (parts[1].equals("HIGH")) {
            digitalWrite(relay_pin, HIGH);
            SerialLogging(1, "Relay is HIGH");
        } else if (parts[1].equals("LOW")) {
            digitalWrite(relay_pin, LOW);
            SerialLogging(1, "Relay is LOW");
        } else {
            SerialLogging(0, "Invalid relay state: " + parts[1]);
        }

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