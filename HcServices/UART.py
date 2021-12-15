import serial
import Constants.Constant as Const
import logging
import threading
from Constracts.ITransport import ITransport


class UART(ITransport):
    __logger: logging.Logger
    __lock: threading.Lock

    def __init__(self, log: logging.Logger):
        super().__init__()
        self.__logger = log
        self.__lock = threading.Lock()

    def connect(self):
        ser = serial.Serial(
            port=Const.UART_PORT,
            baudrate=Const.UART_BAUDRATE,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        return ser

    def receive(self):
        ser = self.connect()
        # bytesToRead = ser.inWaiting()
        # uart_item = ser.read(bytesToRead)
        uart_item = ser.read(24)
        if uart_item:
            self.receive_uart_queue.put(uart_item)

    def send(self, destination, send_data):
        ser = self.connect()
        ser.write(send_data)
        print(f"send uart {destination}: {send_data}")
        self.__logger.info(f"send uart: {send_data}")

    def disconnect(self):
        self.connect().close()

    def reconnect(self):
        self.connect()
        pass
