import zmq
import time
import os
import sys

from load_binary import binaryLoad

device = sys.argv[1]

if __name__ == "__main__":
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:5001")
    time.sleep(0.1)

    acu_instance = binaryLoad(device)
    bytes_read = 0

    while True:

        start_bytes = socket.recv()
        if(start_bytes != bytearray([0xFA, 0xFB, 0xFC])):
            # print("Did not receive start byte")
            continue

        socket.send(bytes([0x02]))

        filename_bytes = socket.recv()

        try:
            filename_bytes.decode()
        except UnicodeDecodeError:
            print("Received invalid filename bytes")
            continue

        print("bytes recv", filename_bytes)
        filename = bytes.decode(filename_bytes)
        print("filename recv", filename)
        if(".bin" not in filename):
            print("Invalid file type")
            continue

        filesize = int.from_bytes(socket.recv(), byteorder='big')
        print("file size", filesize)

        if os.path.exists(filename):
            os.remove(filename)
            print(f"Removed old file: {filename}")


        with open(filename, "wb") as f:
            while bytes_read < filesize:
                packet = socket.recv()
                bytes_read += len(packet)
                f.write(packet)

        print("Finished receiving file, loading to ACU")
        resp = acu_instance.load(filename)
        
        if resp == 0:
            socket.send(bytes([0]))
        else:
            socket.send(bytes([1]))