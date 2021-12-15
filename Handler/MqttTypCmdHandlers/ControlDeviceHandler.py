from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import uuid
from sqlalchemy import and_, bindparam
import threading


class ControlDeviceHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport, uart: ITransport):
        super().__init__(log, mqtt)
        self.__uart = uart

    def handler(self, data):
        method = data['method']
        dev_ID = method[method.find('_') + 1:]
        params = data['params']
        if params:
            cmd_string = f"00 05 {dev_ID} 01 0D 0A"
            msg = bytes.fromhex(cmd_string)
            self.__uart.send(f"{dev_ID}", msg)
            print(msg)
        else:
            cmd_string = f"00 05 {dev_ID} 00 0D 0A"
            msg = bytes.fromhex(cmd_string)
            self.__uart.send(f"{dev_ID}", msg)
        pass
