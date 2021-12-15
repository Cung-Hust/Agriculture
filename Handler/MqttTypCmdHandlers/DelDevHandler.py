from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import uuid
import threading


class DelDevHandler(IMqttTypeCmdHandler):
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

        devices = data.get("Device", [])

        db.Services.DeviceService.RemoveDeviceByCondition(
            db.Table.DeviceTable.c.DeviceAddress.in_(devices)
        )
        db.Services.GroupDeviceMappingService.RemoveGroupDeviceMappingByCondition(
            db.Table.GroupDeviceMappingTable.c.DeviceAddress.in_(devices)
        )
        db.Services.DevicePropertyService.RemoveDevicePropertyMappingByCondition(
            db.Table.DevicePropertyMappingTable.c.DeviceAddress.in_(devices)
        )
        db.Services.EventTriggerOutputDeviceMappingService.RemoveEventTriggerOutputDeviceMappingByCondition(
            db.Table.EventTriggerOutputDeviceMappingTable.c.DeviceAddress.in_(devices)
        )
        db.Services.EventTriggerOutputDeviceSetupValueService.RemoveEventTriggerOutputDeviceSetupValueByCondition(
            db.Table.EventTriggerOutputDeviceSetupValueTable.c.DeviceAddress.in_(devices)
        )
        
        for d in devices:
            cmd_send_to_device = {
                "TYPCMD": data.get("TYPCMD"),
                "Device": d
            }
            self.addControlQueue(cmd_send_to_device)
        self.send_ending_cmd(self.addControlQueue)
        self.waiting_for_handler_cmd()