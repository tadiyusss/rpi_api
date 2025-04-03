#include <PZEM004Tv30.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

//5V --> VU
//RX --> D4
//TX --> D3
//GND -> G

const char* SSID = "EE_GROUP_8";
const char* PASSWORD = "cyrusdavebading_123";
const char* SERVER_IP = "10.3.141.1";
const int SERVER_PORT = 8000;
const char* SENSOR_NAME = "METER_ONE";

const String INIT_URL = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/esp82/initial/";
const String SERVER_URL = String("http://") + SERVER_IP + ":" + String(SERVER_PORT) + "/api/esp82/meter/";

unsigned long DELAY = 1000;

PZEM004Tv30 pzem(D3, D4); // Software Serial pin D3 (RX) & D4 (TX)

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
    String post_data = "name=" + String(SENSOR_NAME) + "&battery_level=100&sensor_type=meter";
    
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

void setup() {
    Serial.begin(9600);
    connectWiFi();

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

    float voltage = pzem.voltage();
    float current = pzem.current();
    float power = pzem.power();
    float energy = pzem.energy();
    float frequency = pzem.frequency();
    float pf = pzem.pf();



    if (!isnan(voltage)) {
        SerialLogging(4, "Voltage: " + String(voltage) + "V");
    } else {
        SerialLogging(0, "Restarting to read voltage.");
        ESP.restart();
    }

    if (!isnan(current)) {
        SerialLogging(4, "Current: " + String(current) + "A");
    } else {
        SerialLogging(0, "Restarting to read current");
        ESP.restart();
    }

    if (!isnan(power)) {
        SerialLogging(4, "Power: " + String(power) + "W");
    } else {
        SerialLogging(0, "Restarting to read power");
        ESP.restart();
    }

    if (!isnan(energy)) {
        SerialLogging(4, "Energy: " + String(energy) + "kWh");
    } else {
        SerialLogging(0, "Restarting to read energy");
        ESP.restart();
    }

    if (!isnan(frequency)) {
        SerialLogging(4, "Frequency: " + String(frequency) + "Hz");
    } else {
        SerialLogging(0, "Restarting to read frequency");
        ESP.restart();
    }

    if (!isnan(pf)) {
        SerialLogging(4, "Power Factor: " + String(pf));
    } else {
        SerialLogging(0, "Restarting to read power factor");
        ESP.restart();
    }


    WiFiClient client;
    HTTPClient http;

    http.begin(client, SERVER_URL);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    String postData = "voltage=" + String(voltage) + "&current=" + String(current) + "&power=" + String(power) + "&energy=" + String(energy) + "&frequency=" + String(frequency) + "&power_factor=" + String(pf) + "&name=" + SENSOR_NAME + "&battery_level=100";

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

        if (delayTime != DELAY) {
            DELAY = delayTime;
            SerialLogging(2, "Setting delay time to " + String(DELAY));
        }
    } else {
        SerialLogging(0, "Error: " + http.errorToString(httpResponseCode));
    }

    Serial.println();
    delay(DELAY);
}