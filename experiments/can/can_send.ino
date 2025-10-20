#define LED_PIN 13

struct CanFrame {
  uint16_t id;
  byte dlc;
  byte data[8];
  bool valid;
};

// --- parser function ---
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

#include <SPI.h>
#include <mcp_can.h>

#define CAN_CS_PIN 10
MCP_CAN CAN(CAN_CS_PIN);

#define SERIAL_BAUD 115200

void setup() {
  pinMode(LED_PIN, OUTPUT);

  Serial.begin(SERIAL_BAUD);
  while (!Serial);

  if (CAN.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ) == CAN_OK) {
    Serial.println("CAN init OK");
  } else {
    Serial.println("CAN init FAIL");
    while (1);
  }

  CAN.setMode(MCP_NORMAL);
  Serial.println("CAN BUS Started");
}


void loop() {
  long unsigned int rxId;
  unsigned char len;
  unsigned char buf[8];

  if (CAN_MSGAVAIL == CAN.checkReceive()) {
    if (CAN.readMsgBuf(&rxId, &len, buf) == CAN_OK) {
      // SLCAN format for standard frames: 't' + 3-digit ID + length + data bytes + '\r'
      if (rxId <= 0x7FF) {
        Serial.print('t');
        Serial.print((rxId >> 8) & 0x07, HEX);
        Serial.print((rxId >> 4) & 0x0F, HEX);
        Serial.print(rxId & 0x0F, HEX);
      } else {
        // SLCAN format for extended frames: 'T' + 8-digit ID + length + data bytes + '\r'
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
}