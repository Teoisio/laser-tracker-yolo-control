#include <Servo.h>

Servo servoPan;
Servo servoTilt;

int SW_PIN = 2;

int joyX = A0;
int joyY = A1;

const int laserPin = 8;

void setup() {
  Serial.begin(115200);
  servoPan.attach(9);
  servoTilt.attach(10);

  pinMode(SW_PIN, INPUT_PULLUP);

  pinMode(laserPin,OUTPUT);
  digitalWrite(laserPin,HIGH);

  servoPan.write(90);
  servoTilt.write(30);
}

void loop() {

  
  if (digitalRead(SW_PIN)==HIGH){ //Automatic mode
  if (Serial.available()){
    String data = Serial.readStringUntil('\n');

    int comma1 = data.indexOf(',');

    if (comma1 > 0){

      int pan = data.substring(0, comma1).toInt();
      int tilt = data.substring(comma1 + 1).toInt();
      

      pan = constrain(pan, 0, 180);
      tilt = constrain(tilt, 0, 90);

      servoPan.write(pan);
      servoTilt.write(tilt);
    }}

  }else{ //Manual mode
  int x = analogRead(joyX); // 0–1023
  int y = analogRead(joyY);

  int pan = map(x, 0, 1023, 0, 180);
  int tilt = map(y, 0, 1023, 0, 90);

  servoPan.write(pan);
  servoTilt.write(tilt);

  delay(10);}

}
