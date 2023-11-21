int servo1 = 5;   // The PWM pin servo1 is attached to
int servo2 = 6;   // The PWM pin servo1 is attached to
int shoot = 7;    // The data pin shoot is attached to

void setup() {
  // Declare pins to be outputs
  pinMode(servo1, OUTPUT);
  pinMode(servo2, OUTPUT);
  pinMode(shoot, OUTPUT);
  // Set serial baud rate
  Serial.begin(115200);
  // Send servos to the middle position
  analogWrite(servo1, 128);
  analogWrite(servo2, 128);
  digitalWrite(shoot, LOW);
}

void loop() {
  if (Serial.available()){
    char device = Serial.read();
    while(!Serial.available()){}
    int command = Serial.read();
    switch(device){
      case 'A': //servo1
        analogWrite(servo1, int(command));  //move to location
      case 'B': //servo2
        analogWrite(servo2, int(command));  //move to location
      case 'C': //shoot
        // turn on and off, shoot
        digitalWrite(shoot, HIGH);
        delay(500);
        digitalWrite(shoot, LOW);
      default:
        break;
    }
  }  
}
