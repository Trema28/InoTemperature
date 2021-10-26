#define PROTO_SOT 0x2
#define PROTO_EOT 0x3

#define CMD_PING 'p'
#define CMD_GETTEMP 'g'

#define PIN_TEMP A0

bool inputAvailable = false;
bool inputComplete = false;
String input = "";

void ledCheck(int time = 1000);

void setup() {
    pinMode(PIN_TEMP, INPUT);
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
            Serial.write(PROTO_SOT);
            Serial.print(CMD_GETTEMP);
            Serial.print(',');
            Serial.print(getTemperature());
            Serial.write(PROTO_EOT);
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

// void sendData(char *data, int len) {
//     Serial.write(PROTO_SOH);
//     Serial.print(len);
//     Serial.write(PROTO_SOT);
//     Serial.print(data);
//     Serial.write(PROTO_EOT);
// }

int getTemperature() {
    return analogRead(PIN_TEMP);
}

void ledCheck(int time) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(time);
    digitalWrite(LED_BUILTIN, LOW);
}
