from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import uuid


class RebootDeviceHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()
        rqi = data.get("RQI")
        mqttReceiveCommandResponse = {
            "RQI": rqi,
            "Rsp": 0
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(mqttReceiveCommandResponse))

        devices = data.get("MAC", [])
        for d in devices:
            cmd_send_to_device = {
                "TYPCMD": data.get("TYPCMD"),
                "MAC": d
            }
            self.addControlQueue(cmd_send_to_device)
        self.send_ending_cmd(self.addControlQueue)
        self.waiting_for_handler_cmd()