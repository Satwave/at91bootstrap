import zmq
import time
import os

from load_binary import binaryLoad


if __name__ == "__main__":
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:5001")
    time.sleep(0.1)

    acu_instance = binaryLoad("/dev/ttyUSB0")
    bytes_read = 0

    while True:

        filename = socket.recv_string()
        print("filename recv", filename)

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


        acu_instance.load(filename)