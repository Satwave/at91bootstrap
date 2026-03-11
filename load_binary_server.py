import zmq
import time

from load_binary import binaryLoad


if __name__ == "__main__":
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind("tcp://*:5555")

    acu_instance = binaryLoad("/dev/ttyUSB0")

    while True:
        filename, data = socket.recv_multipart()

        filename = filename.decode()

        with open(filename, "wb") as f:
            f.write(data)

        print(f"Received file: {filename} ({len(data)} bytes)")

        acu_instance.load(filename)





    data = socket.recv()

    filename = "ACU_bin_" + str(int(time.time())) + ".bin"

    with open("received.bin", "wb") as f:
        f.write(data)

    print("File received")