import zmq
import sys
import os
import time 
from datetime import datetime

BLOCK_SIZE = 16384

context = zmq.Context()
socket = context.socket(zmq.PAIR)

socket.connect("tcp://192.168.5.83:5001")
time.sleep(1)

filepath = sys.argv[1]

timestamp = os.path.getmtime(filepath)
time_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d_%H:%M:%S")

filename = "ACU_firmware_" + time_str + ".bin"
socket.send_string(filename)

filesize = os.path.getsize(filepath)
print(f"Sending {filename}, size: {filesize} bytes")
socket.send(filesize.to_bytes(8, byteorder='big'))

data = []

with open(filepath, "rb") as f:
    while True:
        chunk = f.read(BLOCK_SIZE)
        if not chunk:
            break
        socket.send(chunk) 
        time.sleep(0.01) 