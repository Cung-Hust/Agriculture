from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import uuid
import threading
from Database.Db import Db
import Constants.Constant as Const


class PingGatewayHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()
        with threading.Lock():
            rel = db.Services.NetworkService.FindNetworkById(Const.RIIM_NETWORK_ID)
        network = rel.fetchone()
        res = {
            "RQI": data.get("RQI"),
            "TYPCMD": "PingGateway",
            "MAC": network["GatewayMac"],
            "Success:": True,
	        "Rsp": 0
        }
        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(res))
