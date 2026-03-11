import zmq
import sys
import os
import time

context = zmq.Context()
socket = context.socket(zmq.PUSH)

socket.connect("tcp://192.168.5.83:5555")

filepath = sys.argv[1]
filename = "ACU_firmware_" + str(int(time.time())) + ".bin"

with open(filepath, "rb") as f:
    data = f.read()

socket.send_multipart([
    filename.encode(),
    data
])

print(f"Sent {filename}")