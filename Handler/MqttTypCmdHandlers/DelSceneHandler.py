from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import uuid
import threading


class DelSceneHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()

        mqttReceiveCommandResponse = {
            "RQI": data.get("RQI"),
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
        db.Services.EventTriggerOutputDeviceMappingService.RemoveEventTriggerOutputDeviceMappingByCondition(
            db.Table.EventTriggerOutputDeviceMappingTable.c.EventTriggerId == event_delete
        )
        db.Services.EventTriggerOutputDeviceSetupValueService.RemoveEventTriggerOutputDeviceSetupValueByCondition(
            db.Table.EventTriggerOutputDeviceSetupValueTable.c.EventTriggerId == event_delete
        )
        db.Services.EventTriggerOutputGroupMappingService.RemoveEventTriggerOutputGroupMappingByCondition(
            db.Table.EventTriggerOutputGroupMappingTable.c.EventTriggerId == event_delete
        )
        db.Services.EventTriggerOutputGroupSetupValueService.RemoveEventTriggerOutputGroupSetupValueByCondition(
            db.Table.EventTriggerOutputGroupSetupValueTable.c.EventTriggerId == event_delete
        )
        db.Services.EventTriggerService.RemoveEventTriggerByCondition(
            db.Table.EventTriggerTable.c.EventTriggerId == event_delete
        )

        cmd_send_to_device = {
            "TYPCMD": data.get("TYPCMD"),
            "ID": data.get("ID")
        }
        self.addConfigQueue(cmd_send_to_device)
        self.send_ending_cmd(self.addConfigQueue)
        self.waiting_for_handler_cmd()