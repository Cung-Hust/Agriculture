import asyncio
import time
from Controllers.RdHc import RdHc
import threading
from Database.Db import Db
import logging
from logging.handlers import TimedRotatingFileHandler
from HcServices.Mqtt import Mqtt, MqttConfig
from HcServices.UART import UART
from Handler.MqttDataHandler import MqttDataHandler
import os
from ctypes import *
import Constants.Constant as Const
from Handler.DeviceDataHandler import DeviceDataHandler

file_dir = os.path.dirname(__file__)

logging_handler = logging.handlers.TimedRotatingFileHandler(filename=file_dir + '/Logging/runtime.log', when="MIDNIGHT",
                                                            backupCount=4)
logging_formatter = logging.Formatter(fmt=(
    '%(asctime)s:\t'
    '%(levelname)s:\t'
    '%(filename)s:'
    '%(funcName)s():'
    '%(lineno)d\t'
    '%(message)s'
))
logger = logging.getLogger("my_log")
logging_handler.setFormatter(logging_formatter)
logger.addHandler(logging_handler)
logger.setLevel(logging.DEBUG)

mqttConfig = MqttConfig(
    host=Const.MQTT_HOST, port=Const.MQTT_PORT, qos=Const.MQTT_QOS, keep_alive=Const.MQTT_KEEP_ALIVE,
    username=Const.MQTT_USER, password=Const.MQTT_PASS
)

mqtt = Mqtt(logger, mqttConfig)
uart = UART(logger)

mqtt.connect()
uart.connect()

mqttHandler = MqttDataHandler(logger, mqtt, uart)
uartHandler = DeviceDataHandler(logger, mqtt, uart)

db = Db()
db.init()

hc = RdHc(logger, mqtt, uart, mqttHandler, uartHandler)


def thread_1():
    while True:
        # mqtt.receive()
        hc.hc_handler_mqtt_data()
        time.sleep(0.05)


def thread_2():
    # asyncio.run(hc.hc_thread_report_interval())
    pass


def thread_3():
    while True:
        uart.receive()
        hc.hc_handler_uart_data()
        time.sleep(0.05)


def main():
    threads = list()

    threads.append(threading.Thread(target=thread_1, args=()))
    threads.append(threading.Thread(target=thread_2, args=()))
    threads.append(threading.Thread(target=thread_3, args=()))

    [thread.start() for thread in threads]
    [thread.join() for thread in threads]


if __name__ == "__main__":
    main()
