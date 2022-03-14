#!/usr/bin/env python3


import serial
import serial.tools.list_ports
from typing import Union
from time import sleep

class mySerial():
    def __init__(self):
        self.my_ports  = self.get_availabile_port_list()
        self.connected = False
        self.port = "COM3"
        self.baud_rate = 576000
        self.time_to_wait = 0

        self.ser = None
    def get_availabile_port_list(self) -> Union[list, bool]:
        port_list = list(serial.tools.list_ports.comports())
        if not port_list:
            return False
        else:
            return port_list

    def connect(self, port) -> bool:
        baud_rate    = self.baud_rate
        time_to_wait = self.time_to_wait
        self.ser     = serial.Serial(port=port, baudrate=baud_rate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS, timeout=time_to_wait)
        if not self.ser:
            print("Can't connect to |%s|" % (port))
            return False
        print("Connected to |%s|" % (port) )
        self.connected = True
        return True


    def read_serial(self) -> str:
        return self.ser.read_all()


    def write_to_serial(self, msg: str) -> int:
        """
        Write to serial
        returns: number of bytes written
        """
        print(f"Writing {msg.encode()}")
        num_of_bytes_written = self.ser.write(msg.encode())
        sleep(1)
        return num_of_bytes_written


    def get_port_name(self) -> str:
        return self.ser.name


    def close_serial(self):
        self.ser.close()

