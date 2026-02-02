import serial
import struct
import sys
import os
from xmodem import XMODEM

serial_port = sys.argv[1]
binary_file = sys.argv[2]
RETRY_COUNT = 20

if not os.path.exists(serial_port):
    print(f"Serial device file: {serial_port} does not exist")
    exit(-1)

if not os.path.isfile(binary_file):
    print(f"Binary file: {binary_file} does not exist")
    exit(-1)

with open(binary_file, 'rb') as fp:
    if fp.read(4)[1:] == b"ELF":
        print("Passed in binary is in ELF format. Binary needs to be in binary format")
        exit(-1)

with serial.Serial(serial_port, baudrate=921600, timeout=0.5) as ser:

    putc = lambda data, timeout=1, ser=ser: ser.write(data)
    getc = lambda size, timeout=1, ser=ser: ser.read(size)

    retry_counter = 0
    while True:
        ser.write(b'S')
        first_byte = ser.read(1)
        if first_byte == b'S':
            break
        elif retry_counter >= RETRY_COUNT:
            print(f"Did not recive ack after {RETRY_COUNT} attempts")
            exit(-1)
        else:
            retry_counter += 1

    binary_size = os.path.getsize(binary_file)
    binary_size_packed = struct.pack('I', binary_size)
    ser.write(binary_size_packed)
    if ser.read(4) != binary_size_packed:
        print("Size did not match")
        ser.write(bytes([0]))
        exit(-1)

    ser.write(bytes([69]))
    modem = XMODEM(getc, putc, mode="xmodem1k")
    with open(binary_file, 'rb') as fh:
        print(f"Sending {binary_file} size {binary_size}")
        modem.send(fh)
        print("Wrote binary")
