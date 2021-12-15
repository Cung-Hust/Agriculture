import threading
import uuid
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
from Database.Db import Db
import logging
import json
import Constants.Constant as Const


class CreateGroupHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        mqttReceiveCommandResponse = {
            "RQI": data["RQI"],
            "Rsp": 0
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC,
                       json.dumps(mqttReceiveCommandResponse))

        db = Db()
        groupId = data.get("GroupID")
        devices = data.get("Devices", [])
        devices_address = []
        for d in devices:
            devices_address.append(d.get("Device"))

        rel = db.Services.GroupService.FindGroupByCondition(
            db.Table.GroupTable.c.GroupId == groupId
        )
        group = rel.fetchone()

        if group is None:
            db.Services.GroupService.InsertGroup({"GroupId": groupId})

            group_device_mapping_dict_list = []
            for device in devices:
                group_device_mapping = {
                    "GroupId": groupId,
                    "DeviceAddress": device["Device"],
                    "Number": device["ID"]
                }
                group_device_mapping_dict_list.append(group_device_mapping)
            db.Services.GroupDeviceMappingService.InsertManyGroupDeviceMapping(
                group_device_mapping_dict_list)

        if group is not None:
            group_device_mapping_dict_list = []
            devices_update_list = []
            current_group_devices = []
            rel2 = db.Services.GroupDeviceMappingService.FindGroupDeviceMappingByCondition(
                db.Table.GroupDeviceMappingTable.c.GroupId == groupId
            )
            currentGroupDeviceMapping = rel2.fetchall()
            for c in currentGroupDeviceMapping:
                current_group_devices.append(c["DeviceAddress"])
            devices_duplicate = list(
                set(devices_address).intersection(current_group_devices))
            db.Services.GroupDeviceMappingService.RemoveGroupDeviceMappingByCondition(
                db.Table.GroupDeviceMappingTable.c.DeviceAddress.in_(
                    devices_duplicate)
            )
            for device in devices:
                group_device_mapping = {
                    "GroupId": groupId,
                    "DeviceAddress": device["Device"],
                    "Number": device["ID"],
                    "Success": False
                }
                devices_update_list.append(device["Device"])
                group_device_mapping_dict_list.append(group_device_mapping)

            db.Services.GroupDeviceMappingService.InsertManyGroupDeviceMapping(
                group_device_mapping_dict_list)

        for d in devices:
            cmd_send_to_device = {
                "TYPCMD": data.get("TYPCMD"),
                "GroupID": groupId,
                "Device": d.get("Device"),
                "ID": d.get("ID")
            }
            self.addConfigQueue(cmd_send_to_device)
        self.send_ending_cmd(self.addConfigQueue)
        self.waiting_for_handler_cmd()
