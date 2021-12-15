from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import json
from Database.Db import Db
import uuid
import Constants.Constant as Const
import threading


class ControlRelayHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()
        rqi = data.get("RQI")
        mqttReceiveCommandResponse = {
            "RQI": rqi,
            "Rsp": 0
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC,
                       json.dumps(mqttReceiveCommandResponse))
        # edit by cungdd: chuyen data xuong cho V.A xu ly dieu khien relay
        data.pop("RQI")
        self.addControlQueue(data)
        # --------------

        relays_control = data.get("Control")
        db.Services.GatewayService.UpdateGatewayById(
            Const.GATEWAY_ID, relays_control)

        self.__cmd_res()

    def __cmd_res(self):
        db = Db()
        rel = db.Services.GatewayService.FindGatewayById(Const.GATEWAY_ID)
        gateway = dict(rel.fetchone())
        res = {
            "RQI": str(uuid.uuid4()),
            "TYPCMD": "GWRelayStt",
            "Relay_1": gateway.get("Relay_1"),
            "Relay_2": gateway.get("Relay_2"),
            "Relay_3": gateway.get("Relay_3"),
            "Relay_4": gateway.get("Relay_4"),
            "Scene_1": gateway.get("Scene_1"),
            "Scene_2": gateway.get("Scene_2"),
            "Scene_3": gateway.get("Scene_3"),
            "Scene_4": gateway.get("Scene_4"),
            "Minute_1": gateway.get("Minute_1"),
            "Minute_2": gateway.get("Minute_2"),
            "Minute_3": gateway.get("Minute_3"),
            "Minute_4": gateway.get("Minute_4")
        }
        with threading.Lock():
            self.globalVariable.mqtt_need_response_dict[res["RQI"]] = res
        self.mqtt.send(Const.MQTT_CONTROL_TOPIC,
                       json.dumps(res))
