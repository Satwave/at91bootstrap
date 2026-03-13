import zmq
import sys
import os
import time 
from datetime import datetime

BLOCK_SIZE = 16384

context = zmq.Context()
socket = context.socket(zmq.PAIR)

socket.connect("tcp://192.168.5.83:5001")
time.sleep(.1)


start_bytes = bytearray([0xFA, 0xFB, 0xFC])
socket.send(start_bytes)

if(socket.recv() != bytes([0x02])):
    print("Did not receive ack")
    exit(-1)

filepath = sys.argv[1]

timestamp = os.path.getmtime(filepath)
time_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d_%H:%M:%S")

filename = "ACU_firmware_" + time_str + ".bin"
filename_bytes = filename.encode()
socket.send(filename_bytes)

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

time_wait = time.time()
while(time.time() - time_wait < 60):
    try:
        ack = socket.recv(flags=zmq.NOBLOCK)
        if ack == b'\x00':
            print("Binary Written Successfully")
            exit(0)
        elif ack == b'\x01':
            print("Binary Write Failed")
            exit(-1)
    except zmq.Again:
        continue

print("Did not receive ack after 60 seconds")
