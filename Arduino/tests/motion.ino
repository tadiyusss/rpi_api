// Define PIR sensor pin
#define PIR_SENSOR_PIN D7  // GPIO13 on ESP8266

void setup() {
    Serial.begin(9600);  // Start serial communication
    pinMode(PIR_SENSOR_PIN, INPUT);
    Serial.println("\nPIR Sensor Debugging Started...");
}

void loop() {
    int pirState = digitalRead(PIR_SENSOR_PIN);
    
    Serial.print("PIR Sensor State: ");
    Serial.println(pirState);
    
    if (pirState == HIGH) {
        Serial.println("Motion Detected!");
    } else {
        Serial.println("No Motion");
    }
    
    delay(500);  // Short delay for debugging
}