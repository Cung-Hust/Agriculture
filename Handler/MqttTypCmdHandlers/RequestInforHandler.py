import uuid
import threading
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
from Database.Db import Db
import logging
import json
import Constants.Constant as Const


class RequestInforHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()

        mqttReceiveCommandResponse = {
            "RQI": data["RQI"],
            "Rsp": 0
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC,
                       json.dumps(mqttReceiveCommandResponse))

        rel = db.Services.DeviceService.FindDeviceByCondition(
            db.Table.DeviceTable.c.DeviceAddress.in_(data.get("Device"))
        )
        devices = rel.fetchall()
        devices_info = []
        if devices is not None:
            for device in devices:
                device_info = {
                    "Device": device["DeviceAddress"],
                    "GPS": {
                        "Lat": str(device["Latitude"]),
                        "Long": str(device["Longitude"])
                    },
                    "TXPower": device["TXPower"],
                    "FirmVer": device["FirmwareVersion"]
                }
                devices_info.append(device_info)
        self.__cmd_res(devices_info)

    def __cmd_res(self, devices_info: list):
        res = {
            "RQI": str(uuid.uuid4()),
            "TYPCMD": "DeviceInfo",
            "Devices": devices_info
        }
        with threading.Lock():
            self.globalVariable.mqtt_need_response_dict[res["RQI"]] = res
        self.mqtt.send(Const.MQTT_RESPONSE_TOPIC, json.dumps(res))
