## ESP8266 Sensors and Wi-Fi Documentation

### ESP8266 With SI7021

#### Connections

| SI7021 | ESP8266 |
|--------|---------|
| GND    | GND     |
| 3.3V   | 3.3V    |
| SDA    | D2      |
| SCL    | D1      |

#### Code Setup

In ESP8266' code there are 4 constant values where it should be changed based on your raspberry pi's network configurations and 1 for the send delay.
```
SSID: Name of the network it is connected to or its hotspot name
PASSWORD: Wi-Fi Password
Server IP: IP Address of the raspberry pi
Server Port: Port Address of its web dashboard
Delay: Delay for sending data to the server
```

```
const char* ssid = ""; 
const char* password = "";
const char* serverIP = "";
const int serverPort = 8000;
```

### ESP8266 With PIR Sensor

#### Connections

Sensor facing upwards and the pins are closest to you.

Left to right pins are GND, OUT, VCC.

| PIR Sensor | ESP8266 |
|------------|---------|
| GND        | GND     |
| OUT        | D7      |
| VCC        | 3.3V    |

