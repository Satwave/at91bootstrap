import serial
import struct
import sys
import os
import argparse
from xmodem import XMODEM


class binaryLoad:
    def __init__(self, serial_port):
        self.serial_port = serial_port
        self.RETRY_COUNT = 20

    def load(self, binary_file):
        with serial.Serial(self.serial_port, baudrate=921600, timeout=0.5) as ser:

            putc = lambda data, timeout=1, ser=ser: ser.write(data)
            getc = lambda size, timeout=1, ser=ser: ser.read(size)

            retry_counter = 0
            while True:
                ser.write(b'S')
                first_byte = ser.read(1)
                if first_byte == b'S':
                    ser.timeout = None
                    break
                elif retry_counter >= self.RETRY_COUNT:
                    print(f"Did not recive ack after {self.RETRY_COUNT} attempts")
                    return -1
                else:
                    retry_counter += 1

            binary_size = os.path.getsize(binary_file)
            binary_size_packed = struct.pack('I', binary_size)
            ser.write(binary_size_packed)
            if ser.read(4) != binary_size_packed:
                print("Size did not match")
                ser.write(bytes([0]))
                return -1

            ser.write(bytes([69]))
            modem = XMODEM(getc, putc, mode="xmodem1k")
            with open(binary_file, 'rb') as fh:
                print(f"Sending {binary_file} size {binary_size}")
                modem.send(fh)
                print("Wrote binary")
                return 0
        
        return -1


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Load binary to ACU over serial")

    parser.add_argument("acu_ser", help="ACU serial port")
    parser.add_argument("bin_file", help="Binary file")
    args = parser.parse_args()

    bin_instance = binaryLoad(args.acu_ser)
    bin_instance.load(args.bin_file)



# serial_port = "/dev/tty.usbserial-FT5RH4LZ"
# serial_port = sys.argv[1]
# binary_file = sys.argv[2]
# RETRY_COUNT = 20
# def putc(data, timeout=1):
#     global ser
#     return ser.write(data)
# def getc(size, timeout=1):
#     global ser
#     return ser.read(size)
# ser = serial.Serial(serial_port, baudrate=921600, timeout=0.5)