from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import uuid
import threading


class DelGroupHandler(IMqttTypeCmdHandler):
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

        group_delete = data.get("GroupID")
        device_in_group = []

        rel = db.Services.GroupDeviceMappingService.FindGroupDeviceMappingByCondition(
            db.Table.GroupDeviceMappingTable.c.GroupId == group_delete
        )

        for r in rel:
            device_in_group.append(r["DeviceAddress"])

        db.Services.GroupDeviceMappingService.RemoveGroupDeviceMappingByCondition(
            db.Table.GroupDeviceMappingTable.c.GroupId == group_delete
        )

        for d in device_in_group:
            cmd_send_to_device = {
                "TYPCMD": "DelDevFrGroup",
                "GroupId": group_delete,
                "Device": d
            }
            self.addConfigQueue(cmd_send_to_device)
        self.send_ending_cmd(self.addConfigQueue)
        self.waiting_for_handler_cmd()
      