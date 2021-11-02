#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 4
#define TEMPERATURE_PRECISION 12

#define HELLO_WORD 'A'
#define CMD_PING 'p'
#define CMD_GETTEMP 'g'

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensor(&oneWire);
DeviceAddress Thermometer;

void setup() {
    Serial.begin(9600);

    while (Serial.available() <= 0) {
        Serial.println(HELLO_WORD);
        ledCheck();
    }
    while (Serial.available()) {
        Serial.read();
    }

    sensor.begin();
    sensor.getAddress(Thermometer, 0);
    sensor.setResolution(Thermometer, TEMPERATURE_PRECISION);
}

void loop() {
    if (Serial.available()) {
        char input = (char)Serial.read();

        if (input == CMD_PING) {
            Serial.println(String(millis()));
        }
        else if (input == CMD_GETTEMP) {
            Serial.println(String(getTemperature()));
        }
    }
}

float getTemperature() {
    sensor.requestTemperatures();
    return sensor.getTempC(Thermometer);
}

void ledCheck() {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(200);
    digitalWrite(LED_BUILTIN, LOW);
    delay(100);
}
