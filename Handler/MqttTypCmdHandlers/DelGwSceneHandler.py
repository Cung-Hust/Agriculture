import uuid
import threading
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
from Database.Db import Db
import logging
import json
import Constants.Constant as Const


class DelGwSceneHandler(IMqttTypeCmdHandler):
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
        
        event_delete = data.get("ID")
        db.Services.EventTriggerInputDeviceSetupValueService.RemoveEventTriggerInputDeviceSetupValueByCondition(
            db.Table.EventTriggerInputDeviceSetupValueTable.c.EventTriggerId == event_delete
        )
        db.Services.EventTriggerInputDeviceMappingService.RemoveEventTriggerInputDeviceMappingByCondition(
            db.Table.EventTriggerInputDeviceMappingTable.c.EventTriggerId == event_delete
        )
        db.Services.GatewayEventTriggerOutputRelayService.RemoveEventTriggerOutputRelayByCondition(
            db.Table.GatewayEventTriggerOutputRelayTable.c.EventTriggerId == event_delete
        )
        db.Services.GatewayEventTriggerService.RemoveGatewayEventTriggerByCondition(
            db.Table.GatewayEventTriggerTable.c.EventTriggerId == event_delete
        )

        cmd_send_to_device = {
            "TYPCMD": data.get("TYPCMD"),
            "ID": data.get("ID")
        }
        self.addConfigQueue(cmd_send_to_device)
        self.send_ending_cmd(self.addConfigQueue)
        self.waiting_for_handler_cmd()