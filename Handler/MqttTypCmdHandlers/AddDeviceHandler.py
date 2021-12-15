import uuid
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import threading
import time


class AddDeviceHandler(IMqttTypeCmdHandler):
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

        current_devices_list = []

        with threading.Lock():
            rel = db.Services.DeviceService.FindAllDevice()
        devices_record = rel.fetchall()
        for d in devices_record:
            current_devices_list.append(d["DeviceAddress"])
        devices_add = list(set(data.get("Device", [])) -
                           set(current_devices_list))
        devices_same = list(
            set(data.get("Device", [])).intersection(current_devices_list))
        devices_data_add = []
        devices_property_mapping_add = []
        cmd_res_to_cloud_add = []
        if devices_add:
            for d in devices_add:
                devices_data_add.append({
                    'DeviceAddress': d,
                    'Ip': "121212121212",
                    'NetKey': "",
                    'PanId_1': "",
                    'PanId_2': "",
                    'Longitude': "0",
                    'Latitude': "0",
                    'TXPower': int(),
                    'VMax': float(),
                    'VMin': float(),
                    'IMax': float(),
                    'IMin': float(),
                    'CosMax': float(),
                    'CosMin': float(),
                    'PMax': float(),
                    'PMin': float(),
                    'TMax': int(),
                    'TMin': int(),
                    'LMax': float(),
                    'LMin': float(),
                    'ActiveTime': int(),
                    'UpdateTime': int(),
                    'CurrentRunningScene': int(),
                    'Status': int(),
                    'IsOnline': False,
                    'IsSync': True,
                    'DimInit': int(),
                    'PRating': int(),
                    'KWH': float(),
                    'FirmwareVersion': "1.1",
                    'Timeslot': 0,
                    'RelayCurrent': 0,
                    'DimCurrent': 0,
                    'SceneCurrent': -1,
                    'CosCurrent': 0,
                    'VCurrent': 0,
                    'ICurrent': 0,
                    'PCurrent': 0,
                    'KWhCurrent': 0,
                    'TCurrent': 0,
                    'LuxCurrent': 0

                })
                devices_property_mapping_add.append({
                    "DeviceAddress": d,
                    "PropertyId": Const.PROPERTY_RELAY_ID,
                    "PropertyValue": 0
                })
                devices_property_mapping_add.append({
                    "DeviceAddress": d,
                    "PropertyId": Const.PROPERTY_DIM_ID,
                    "PropertyValue": 0
                })

            with threading.Lock():
                db.Services.DeviceService.InsertMany(devices_data_add)
                db.Services.DevicePropertyService.InsertManyDevicePropertyMapping(
                    devices_property_mapping_add)
