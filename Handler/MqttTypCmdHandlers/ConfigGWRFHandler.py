import time
import uuid
import threading
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import Constants.Constant as Const
import json
import logging
from Database.Db import Db
import asyncio


class ConfigGWRFHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    # async def handler(self, data):
    def handler(self, data):
        self.__receive_mess_res(data)

        db = Db()
        rel = db.Services.NetworkService.FindNetworkById(Const.RIIM_NETWORK_ID)
        network = rel.fetchone()
        if network is None:
            db.Services.NetworkService.InsertNetwork({
                "NetworkId": Const.RIIM_NETWORK_ID,
                "NetworkKey": data.get("Netkey"),
                "TXPower": data.get("TXPower")
            })
        if network is not None:
            if network["NetworkKey"] != data.get("Netkey"):
                with threading.Lock():
                    db.Services.NetworkService.UpdateNetworkByCondition(
                        db.Table.NetworkTable.c.NetworkId == Const.RIIM_NETWORK_ID, {"NetworkKey": data.get("Netkey")})

            if network["TXPower"] != data.get("TXPower"):
                with threading.Lock():
                    db.Services.NetworkService.UpdateNetworkByCondition(
                        db.Table.NetworkTable.c.NetworkId == Const.RIIM_NETWORK_ID, {"TXPower": data.get("TXPower")})
        self.__cmd_res()

        data.pop("RQI")
        self.addConfigQueue(data)
        self.send_ending_cmd(self.addConfigQueue)
        self.waiting_for_handler_cmd()

    def __receive_mess_res(self, data):
        mqttReceiveCommandResponse = {
            "RQI": data.get("RQI"),
            "Rsp": 0
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC,
                       json.dumps(mqttReceiveCommandResponse))

    def __cmd_res(self):
        db = Db()
        with threading.Lock():
            rel = db.Services.NetworkService.FindNetworkById(
                Const.RIIM_NETWORK_ID)
        network = dict(rel.fetchone())
        res = {
            "RQI": str(uuid.uuid4()),
            "TYPCMD": "NetInfor",
            "NETKEY": network.get("NetworkKey"),
            "TXPower": network.get("TXPower"),
            "MAC": network.get("GatewayMac"),
            "FirmVer": network.get("FirmwareVersion")
        }
        with threading.Lock():
            self.globalVariable.mqtt_need_response_dict[res["RQI"]] = res
        self.mqtt.send(Const.MQTT_CONTROL_TOPIC, json.dumps(res))
