from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import json
from Helper.Terminal import Terminal
import Constants.Constant as Const


class GatewayCommanderHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        t = Terminal()
        rel = t.execute_with_result(data["Command"])
        mes_res = {
                "RQI": data["RQI"],
                "Rsp": 0,
                "TYPCMD": "GatewayCmdRsp",
                "Response": rel[1]
            }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(mes_res))

