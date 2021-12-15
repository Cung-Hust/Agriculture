import threading
import uuid

from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import json
import Constants.Constant as Const
from Database.Db import Db
from sqlalchemy import and_


class DelDevFrGroupHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        mqttReceiveCommandResponse = {
            "RQI": data["RQI"],
            "Rsp": 0
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(mqttReceiveCommandResponse))

        db = Db()

        devices = data.get("Device", [])
        groupId = data.get("GroupID", [])

        db.Services.GroupDeviceMappingService.RemoveGroupDeviceMappingByCondition(
            and_(db.Table.GroupDeviceMappingTable.c.GroupId == groupId,
                 db.Table.GroupDeviceMappingTable.c.DeviceAddress.in_(devices)
                 )
        )
        
        for d in devices:
            cmd_send_to_device = {
                "TYPCMD": data.get("TYPCMD"),
                "GroupId": groupId,
                "Device": d
            }
            self.addConfigQueue(cmd_send_to_device)
        self.send_ending_cmd(self.addConfigQueue)
        self.waiting_for_handler_cmd()
     