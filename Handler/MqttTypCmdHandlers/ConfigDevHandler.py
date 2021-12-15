import uuid
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import threading
import time


class ConfigDevHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()

        mqttReceiveCommandResponse = {
            "RQI": data.get("RQI"),
            "Rsp": 0
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC,
                       json.dumps(mqttReceiveCommandResponse))

        groups: list
        devices: list

        groups = data.get("Group", [])
        devices = data.get("Device", [])

        with threading.Lock():
            rel = db.Services.GroupDeviceMappingService.FindGroupDeviceMappingByCondition(
                db.Table.GroupDeviceMappingTable.c.GroupId.in_(groups)
            )

        for r in rel:
            devices.append(r["DeviceAddress"])

        unique_devices = set(devices)
        update_data = {}

        if data.get("PRating") is not None:
            update_data["PRating"] = data.get("PRating")
        if data.get("TXPower") is not None:
            update_data["TXPower"] = data.get("TXPower")
        if data.get("DimInit") is not None:
            update_data["DimInit"] = data.get("DimInit")
        if data.get("VMax") is not None:
            update_data["VMax"] = data.get("VMax")
        if data.get("VMin") is not None:
            update_data["VMin"] = data.get("VMin")
        if data.get("IMax") is not None:
            update_data["IMax"] = data.get("IMax")
        if data.get("IMin") is not None:
            update_data["IMin"] = data.get("IMin")
        if data.get("CosMax") is not None:
            update_data["CosMax"] = data.get("CosMax")
        if data.get("CosMin") is not None:
            update_data["CosMin"] = data.get("CosMin")
        if data.get("Pmax") is not None:
            update_data["PMax"] = data.get("Pmax")
        if data.get("Pmin") is not None:
            update_data["PMin"] = data.get("Pmin")
        if data.get("TMax") is not None:
            update_data["TMax"] = data.get("TMax")
        if data.get("TMin") is not None:
            update_data["TMin"] = data.get("TMin")

        if update_data:
            with threading.Lock():
                db.Services.DeviceService.UpdateDeviceByCondition(
                    db.Table.DeviceTable.c.DeviceAddress.in_(
                        unique_devices), update_data
                )

        result = {
            "devices_success": unique_devices,
            "devices_failure": []
        }
        self.__cmd_res(result, data)

        for d in devices:
            cmd_send_to_device = update_data
            cmd_send_to_device["TYPCMD"] = data.get("TYPCMD")
            cmd_send_to_device["Device"] = d
            cmd_send_to_device["Rollback"] = data.get("Rollback")
            cmd_send_to_device["CheckDelay"] = data.get("CheckDelay")
            self.addConfigQueue(cmd_send_to_device)

        for g in groups:
            cmd_send_to_device = update_data
            cmd_send_to_device["TYPCMD"] = data.get("TYPCMD")
            cmd_send_to_device["Group"] = g
            self.addConfigQueue(cmd_send_to_device)
        self.send_ending_cmd(self.addConfigQueue)
        self.waiting_for_handler_cmd()

    def __cmd_res(self, result: dict, data):
        db = Db()
        res = {
            "RQI": str(uuid.uuid4()),
            "TYPCMD": "DeviceConfig",
            "Devices": []
        }
        with threading.Lock():
            rel = db.Services.DeviceService.FindDeviceByCondition(
                db.Table.DeviceTable.c.DeviceAddress.in_(
                    result["devices_success"])
            )

        for d in rel:
            temp = {
                "Device": d["DeviceAddress"],
                "PRating": d["PRating"],
                "TXPower": d["TXPower"],
                "DimInit": d["DimInit"],
                "VMax": d["VMax"],
                "VMin": d["VMin"],
                "IMax": d["IMax"],
                "IMin": d["IMin"],
                "CosMax": d["CosMax"],
                "CosMin": d["CosMin"],
                "Pmax": d["PMax"],
                "Pmin": d["PMin"],
                "TMax": d["TMax"],
                "TMin": d["TMin"],
                "CheckDelay": data.get("CheckDelay"),
                "Rollback": data.get("Rollback")
            }
            res["Devices"].append(temp)
        with threading.Lock():
            self.globalVariable.mqtt_need_response_dict[res["RQI"]] = res
        self.mqtt.send(Const.MQTT_RESPONSE_TOPIC,
                       json.dumps(res))
