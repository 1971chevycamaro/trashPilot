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

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(1000000);
  Serial.println("Ready for CAN serial messages...");
}

void loop() {
  if (Serial.available()) {
    String s = Serial.readStringUntil('\r');
    CanFrame f = parseSlcan(s);

    if (f.valid) {
      // Example action: LED control
      if (f.id == 0x100 && f.data[0] == 0x01) digitalWrite(LED_PIN, HIGH);
      if (f.id == 0x100 && f.data[0] == 0x00) digitalWrite(LED_PIN, LOW);
    }
  }
}