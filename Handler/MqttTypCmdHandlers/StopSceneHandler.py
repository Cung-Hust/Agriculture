import uuid
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import threading


class StopSceneHandler(IMqttTypeCmdHandler):
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

        devices_stop_list = data.get("Device", [])
        groups_stop_list = data.get("group", [])

        db.Services.EventTriggerOutputDeviceMappingService.UpdateEventTriggerOutputDeviceMappingByCondition(
            db.Table.EventTriggerOutputDeviceMappingTable.c.DeviceAddress.in_(devices_stop_list),
            {
                "IsEnable": False
            }
        )

        db.Services.EventTriggerOutputGroupMappingService.UpdateEventTriggerOutputGroupMappingByCondition(
            db.Table.EventTriggerOutputGroupMappingTable.c.GroupId.in_(groups_stop_list),
            {
                "IsEnable": False
            }
        )

        for d in devices_stop_list:
            cmd_send_to_device = {
                "TYPCMD": "StopDevScene",
                "ID": data.get("ID"),
                "Device": d
            }
            self.addConfigQueue(cmd_send_to_device)

        for g in groups_stop_list:
            cmd_send_to_device = {
                "TYPCMD": "StopGroupScene",
                "ID": data.get("ID"),
                "group": g
            }
            self.addConfigQueue(cmd_send_to_device)
        self.send_ending_cmd(self.addConfigQueue)
        self.waiting_for_handler_cmd()