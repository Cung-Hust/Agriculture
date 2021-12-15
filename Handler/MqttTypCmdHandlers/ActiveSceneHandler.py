from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import uuid
import threading


class ActiveSceneHandler(IMqttTypeCmdHandler):
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

        devices_start_list = data.get("Device", [])
        groups_start_list = data.get("group", [])

        with threading.Lock():
            db.Services.EventTriggerOutputDeviceMappingService.UpdateEventTriggerOutputDeviceMappingByCondition(
                db.Table.EventTriggerOutputDeviceMappingTable.c.DeviceAddress.in_(
                    devices_start_list),
                {
                    "IsEnable": True
                }
            )

            db.Services.EventTriggerOutputGroupMappingService.UpdateEventTriggerOutputGroupMappingByCondition(
                db.Table.EventTriggerOutputGroupMappingTable.c.GroupId.in_(
                    groups_start_list),
                {
                    "IsEnable": True
                }
            )
        for d in devices_start_list:
            cmd_send_to_device = {
                "TYPCMD": "ActiveDevScene",
                "ID": data.get("ID"),
                "Device": d
            }
            self.addControlQueue(cmd_send_to_device)

        for g in groups_start_list:
            cmd_send_to_device = {
                "TYPCMD": "ActiveGroupScene",
                "ID": data.get("ID"),
                "group": g
            }
            self.addControlQueue(cmd_send_to_device)
        self.send_ending_cmd(self.addControlQueue)
        self.waiting_for_handler_cmd()
