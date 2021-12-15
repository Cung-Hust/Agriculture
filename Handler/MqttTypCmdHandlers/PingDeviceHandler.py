from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import uuid

from Handler.DeviceDataHandler import DeviceDataHandler


class PingDeviceHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        res_success = {
            "RQI": data.get("RQI"),
            "TYPCMD": "PingDeviceRsp",
            "Device": data.get("Device"),
            "Success": True
        }

        res_failure = {
            "RQI": data.get("RQI"),
            "TYPCMD": "PingDeviceRsp",
            "Device": data.get("Device"),
            "Success": False
        }

        cmd_send_to_device = {
            "RQI": data.get("RQI"),
            "TYPCMD": "PingDeviceRsp",
            "Device": data.get("Device")
        }

        self.addControlQueue(cmd_send_to_device)
        self.send_ending_cmd(self.addControlQueue)
        self.waiting_for_handler_cmd()
