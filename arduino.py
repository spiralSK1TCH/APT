import serial
import serial.tools.list_ports
import time
hexnum = hex(255)
print(int(hexnum,base=16))
print(b"")
ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p)
# Open port at 115200 baud rate
arduinoPort = serial.Serial("/dev/ttyACM1", 115200)     
# Wait for connection to settle
def writeToArduino(servo,degree):
    pass
time.sleep(1)
arduinoPort.write(b"A")
arduinoPort.write(b"A")