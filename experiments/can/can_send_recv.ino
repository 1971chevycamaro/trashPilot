#include <Servo.h>
#include <SPI.h>
#include <mcp_can.h>

// === ESC SETTINGS ===
#define ESC_MAX 2000
#define ESC_MIN 1000
#define ESC_NEUTRAL 1550
#define ESC_BRAKE_TRANSITION_TIME_STEP 70
#define ESC_REVERSE_EFFORT_COMPENSATION 1.4

#define COMMAND_TIMEOUT_MS 500   // <-- time before auto-neutral (ms)

// === CAN SETTINGS ===
#define LED_PIN 13
#define SERIAL_BAUD 115200
#define CAN_CS_PIN 10
MCP_CAN CAN(CAN_CS_PIN);

struct CanFrame {
  uint16_t id;
  byte dlc;
  byte data[8];
  bool valid;
};

// --- parser for SLCAN 't' frames ---
CanFrame parseSlcan(const String &frame) {
  CanFrame f = {0, 0, {0}, false};

  if (frame.length() < 5 || frame[0] != 't') return f;

  char idStr[4];
  frame.substring(1, 4).toCharArray(idStr, 4);
  f.id = strtol(idStr, NULL, 16);

  f.dlc = frame[4] - '0';
  if (f.dlc > 8) return f;

  for (byte i = 0; i < f.dlc; i++) {
    if (5 + i * 2 + 1 >= frame.length()) return f;
    char b[3];
    frame.substring(5 + i * 2, 7 + i * 2).toCharArray(b, 3);
    f.data[i] = strtol(b, NULL, 16);
  }

  f.valid = true;
  return f;
}

Servo esc;
bool wasForward = false;
unsigned long lastCommandTime = 0;

void neutral() {
  esc.writeMicroseconds(ESC_NEUTRAL);
}

void forward(int effort) {
  esc.writeMicroseconds(ESC_NEUTRAL + effort);
  wasForward = true;
}

void backward(int effort) {
  if (wasForward) {
    esc.writeMicroseconds(ESC_NEUTRAL - 100);  // brake
    delay(ESC_BRAKE_TRANSITION_TIME_STEP);
    esc.writeMicroseconds(ESC_NEUTRAL);        // neutral
    delay(ESC_BRAKE_TRANSITION_TIME_STEP);
    wasForward = false;
  }
  esc.writeMicroseconds(ESC_NEUTRAL - (effort * ESC_REVERSE_EFFORT_COMPENSATION));
}

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(SERIAL_BAUD);
  while (!Serial);

  esc.attach(9, ESC_MIN, ESC_MAX);
  esc.writeMicroseconds(ESC_NEUTRAL);
  delay(1000);

  if (CAN.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ) == CAN_OK) {
    Serial.println("CAN init OK");
  } else {
    Serial.println("CAN init FAIL");
    while (1);
  }

  CAN.setMode(MCP_NORMAL);
  Serial.println("CAN BUS Started");
  lastCommandTime = millis();
}

void loop() {
  // --- auto-neutral watchdog ---
  if (millis() - lastCommandTime > COMMAND_TIMEOUT_MS) {
    neutral();
  }

  // --- CAN RECEIVE FOR SERIAL OUTPUT ---
  long unsigned int rxId;
  unsigned char len;
  unsigned char buf[8];
  if (CAN_MSGAVAIL == CAN.checkReceive()) {
    if (CAN.readMsgBuf(&rxId, &len, buf) == CAN_OK) {
      // SLCAN encode
      if (rxId <= 0x7FF) {
        Serial.print('t');
        Serial.print((rxId >> 8) & 0x07, HEX);
        Serial.print((rxId >> 4) & 0x0F, HEX);
        Serial.print(rxId & 0x0F, HEX);
      } else {
        Serial.print('T');
        for (int i = 28; i >= 0; i -= 4) {
          Serial.print((rxId >> i) & 0xF, HEX);
        }
      }
      Serial.print(len, HEX);
      for (int i = 0; i < len; i++) {
        if (buf[i] < 0x10) Serial.print('0');
        Serial.print(buf[i], HEX);
      }
      Serial.print('\r');
    }
  }

  // --- SERIAL RECEIVE: COMMANDS FROM COMPUTER ---
  if (Serial.available()) {
    String s = Serial.readStringUntil('\r');
    CanFrame f = parseSlcan(s);

    if (f.valid) {
      if (f.id == 0x363) {
        // interpret data bytes as steering effort control
        int effort = f.data[0];  // 0–255 range
        int dir = f.data[1];     // 0=neutral, 1=fwd, 2=rev

        if (dir == 0) neutral();
        else if (dir == 1) forward(effort);
        else if (dir == 2) backward(effort);
        lastCommandTime = millis(); // reset watchdog
      }
    }
  }
}
