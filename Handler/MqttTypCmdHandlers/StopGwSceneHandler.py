import uuid
import threading
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
from Database.Db import Db
import logging
import json
import Constants.Constant as Const


class StopGwSceneHandler(IMqttTypeCmdHandler):
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

        # print(data)
        db.Services.GatewayEventTriggerService.UpdateGatewayEventTriggerCondition(
            db.Table.GatewayEventTriggerTable.c.EventTriggerId == data.get('ID'),
            {
                "IsEnable": False
            }
        )

        cmd_send_to_device = {
            "TYPCMD": "StopGWScene",
            "ID": data.get("ID"),
        }
        self.addConfigQueue(cmd_send_to_device)

        self.send_ending_cmd(self.addConfigQueue)
        self.waiting_for_handler_cmd()
