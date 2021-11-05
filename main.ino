#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 4
#define TEMPERATURE_PRECISION 12

#define CONN_REQ 'A'
#define CMD_PING 'p'
#define CMD_GETTEMP 'g'

OneWire oneWire(ONE_WIRE_BUS);

DallasTemperature sensor(&oneWire);
int devicesNum = 0;

void setup() {
    Serial.begin(9600);

    sensor.begin();
    sensor.setResolution(TEMPERATURE_PRECISION);

    devicesNum = sensor.getDeviceCount();
}

void loop() {
    if (Serial.available()) {
        char input = (char)Serial.read();

        if (input == CMD_PING) {
            Serial.println(String(millis()));
        }
        else if (input == CMD_GETTEMP) {
            printTemperatures();
        }
        else if (input == CONN_REQ) {
            Serial.println(CONN_REQ);
        }
    }
}

void printTemperatures() {
    sensor.requestTemperatures();
    for (int i = 0; i < devicesNum; ++i) {
        Serial.print(sensor.getTempCByIndex(i));
        Serial.print(' ');
    }
    Serial.println(' ');
}
