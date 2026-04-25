#include <Servo.h>

Servo servoPan;
Servo servoTilt;

const int laserPin = 8;

void setup() {
  Serial.begin(115200);
  servoPan.attach(9);
  servoTilt.attach(10);
  pinMode(laserPin, OUTPUT);
  digitalWrite(laserPin, LOW);
  servoPan.write(90);
  servoTilt.write(90);
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');

    int comma1 = data.indexOf(',');
    int comma2 = data.indexOf(',', comma1 + 1);

    if (comma1 > 0 && comma2 > 0) {
      int pan   = constrain(data.substring(0, comma1).toInt(), 0, 180);
      int tilt  = constrain(data.substring(comma1 + 1, comma2).toInt(), 0, 180);
      int laser = data.substring(comma2 + 1).toInt();

      servoPan.write(pan);
      servoTilt.write(tilt);
      digitalWrite(laserPin, laser ? HIGH : LOW);
    }
  }
}