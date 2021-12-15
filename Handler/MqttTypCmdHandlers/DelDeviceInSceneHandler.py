import uuid
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
from sqlalchemy import and_
import threading


class DelDeviceInSceneHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()

        mqttReceiveCommandResponse = {
            "RQI": data.get("RQI"),
            "Rsp":0
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(mqttReceiveCommandResponse))

        devices_delete_list = data.get("Device", [])
        groups_delete_list = data.get("group", [])

        db.Services.EventTriggerOutputDeviceMappingService.RemoveEventTriggerOutputDeviceMappingByCondition(
            and_(
                db.Table.EventTriggerOutputDeviceMappingTable.c.EventTriggerId == data.get("ID"),
                db.Table.EventTriggerOutputDeviceMappingTable.c.DeviceAddress.in_(devices_delete_list)
            )
        )

        db.Services.EventTriggerOutputDeviceSetupValueService.RemoveEventTriggerOutputDeviceSetupValueByCondition(
            and_(
                db.Table.EventTriggerOutputDeviceSetupValueTable.c.EventTriggerId == data.get("ID"),
                db.Table.EventTriggerOutputDeviceSetupValueTable.c.DeviceAddress.in_(devices_delete_list)
            )
        )

        db.Services.EventTriggerOutputGroupMappingService.RemoveEventTriggerOutputGroupMappingByCondition(
            and_(
                db.Table.EventTriggerOutputGroupMappingTable.c.EventTriggerId == data.get("ID"),
                db.Table.EventTriggerOutputGroupMappingTable.c.GroupId.in_(groups_delete_list)
            )
        )

        db.Services.EventTriggerOutputGroupSetupValueService.RemoveEventTriggerOutputGroupSetupValueByCondition(
            and_(
                db.Table.EventTriggerOutputGroupSetupValueTable.c.EventTriggerId == data.get("ID"),
                db.Table.EventTriggerOutputGroupSetupValueTable.c.GroupId.in_(groups_delete_list)
            )
        )

        for d in devices_delete_list:
            cmd_send_to_device = {
                "TYPCMD": "DelDeviceInScene",
                "ID": data.get("ID"),
                "Device": d
            }
            self.addConfigQueue(cmd_send_to_device)

        for g in groups_delete_list:
            cmd_send_to_device = {
                "TYPCMD": "DelGroupInScene",
                "ID": data.get("ID"),
                "group": g
            }
            self.addConfigQueue(cmd_send_to_device)
        self.send_ending_cmd(self.addConfigQueue)
        self.waiting_for_handler_cmd()
