#include <Servo.h>

Servo servo1;
Servo servo2;

const int shoot = 7;    // The data pin shoot is attached to

void setup() {
  // attach servos to pins
  servo1.attach(5);
  servo2.attach(6);
  // Declare pins to be outputs
  pinMode(shoot, OUTPUT);
  // Set serial baud rate
  Serial.begin(115200);
  // Send servos to the middle position
  servo1.write(90);
  delay(30);
  servo2.write(90);
  delay(30);
  // Make sure it doesnt shoot on startup
  digitalWrite(shoot, LOW);
}

void loop() {
  // If serial port sends data
  if (Serial.available()) {
    // Take input and hold it as the device
    char device = Serial.read();
    // Wait until more data is recieved
    while(!Serial.available()){}
    // Call this data the command
    int command = Serial.read();
    switch (device) {
      case 'A': // Servo1
        servo1.write(command);  // Move to location
        break;
      case 'B': //servo2
        servo2.write(command);  // Move to location
        break;
      case 'C':
        digitalWrite(shoot, HIGH);
        delay(500);
        digitalWrite(shoot, LOW);
        break;
      default:
        break;
    }
  }
}
