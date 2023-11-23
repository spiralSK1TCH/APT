import serial
import time
import zmq

def writeToArduino(servo, degree=90):
    arduinoPort.write(servo.encode())
    arduinoPort.write(bytes([degree]))

# Open port at 115200 baud rate
arduinoPort = serial.Serial("/dev/ttyACM1", 115200)     

# Set up server to tcp port
# Get context to set up the TCP port
context = zmq.Context()
# Create a reply socket on this port
socket = context.socket(zmq.REP)
# Bind the reply socket to the TCP port
socket.bind("tcp://*:5555")

# Wait for connection to settle
time.sleep(2)

while True:
    # Wait for next request from client
    message = socket.recv()
    print(message)
    print(f"Received request: {message}")
    if message == b"X":
        break
    writeToArduino(message[0], message[1])
    # Send Confirmation to client
    socket.send_string(f"Moved {message[0]} to {message[1]}")
print("done")
arduinoPort.close()
socket.close()
exit(0)
