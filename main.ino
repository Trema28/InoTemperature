#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 4
#define TEMPERATURE_PRECISION 12

#define PROTO_SOT 0x2
#define PROTO_EOT 0x3

#define CMD_PING 'p'
#define CMD_GETTEMP 'g'

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensor(&oneWire);
DeviceAddress Thermometer;

bool inputAvailable = false;
bool inputComplete = false;
String input = "";

// void ledCheck(int time = 1000);

void setup() {
    sensor.begin();
    sensor.getAddress(Thermometer, 0);
    sensor.setResolution(Thermometer, TEMPERATURE_PRECISION);

    Serial.begin(9600);
    input.reserve(20);
}

void loop() {
    if (inputComplete) {
        if (input[0] == CMD_PING) {
            Serial.write(PROTO_SOT);
            Serial.print(CMD_PING);
            Serial.print(',');
            Serial.print(millis());
            Serial.write(PROTO_EOT);
        }
        else if (input[0] == CMD_GETTEMP) {
            // Serial.write(PROTO_SOT);
            // Serial.print(CMD_GETTEMP);
            // Serial.print(',');
            // Serial.print(String(getTemperature()));
            // Serial.write(PROTO_EOT);
            Serial.println(String(getTemperature()));
        }

        input = "";
        inputComplete = false;
    }
}

void serialEvent() {
    while (Serial.available()) {
        char inp = (char)Serial.read();

        if (!inputAvailable && inp == PROTO_SOT) {
            inputAvailable = true;
            continue;
        }

        if (inp == PROTO_EOT) {
            inputComplete = true;
            inputAvailable = false;
            break;
        }

        input += inp;
    }
}

float getTemperature() {
    sensor.requestTemperatures();
    return sensor.getTempC(Thermometer);
}

// void ledCheck(int time) {
//     digitalWrite(LED_BUILTIN, HIGH);
//     delay(time);
//     digitalWrite(LED_BUILTIN, LOW);
// }
