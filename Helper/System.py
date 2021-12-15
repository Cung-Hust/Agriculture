import threading
from Database.Db import Db
import logging
from GlobalVariables.GlobalVariables import GlobalVariables
import uuid
import Constants.Constant as Const
import datetime
import time

import re
import uuid


class System:
    __globalVariables = GlobalVariables()
    __logger = logging.Logger
    __db = Db()

    def __init__(self, logger: logging.Logger):
        self.__logger = logger

    def send_device_report(self) -> dict:
        timestamp_now = time.time()
        t = datetime.datetime.fromtimestamp(timestamp_now).strftime("%Y%m%d")

        res = {
            "RQI": str(uuid.uuid4()),
            "TYPCMD": "DeviceReport",
            "Day": t,
            "KWh": int(),
            "Minute": int(),
            "Devices": []
        }
        with threading.Lock():
            rel = self.__db.Services.DeviceService.FindAllDevice()
        devices = rel.fetchall()
        for d in devices:
            res["Devices"].append({
                "Device": d["DeviceAddress"],
                "KWh": 0,
                "Minute": 0
            })
        with threading.Lock():
            self.__globalVariables.mqtt_need_response_dict[res["RQI"]] = res
        return res

    def add_gateway_event_log(self):
        res = {
            "RQI": str(uuid.uuid4()),
            "TYPCMD": "GwEventLog",
            "LogType": 1,
            "LogStatus": 1,
            "LogData": "gateway start"
        }
        return res

    def add_basic_info_to_db(self):
        rel = self.__db.Services.GatewayService.FindGatewayById(
            Const.GATEWAY_ID)
        gateway = rel.fetchone()

        rel2 = self.__db.Services.NetworkService.FindNetworkById(
            Const.RIIM_NETWORK_ID)
        network = rel2.fetchone()

        if gateway is None:
            self.__db.Services.GatewayService.InsertGateway({
                "GatewayId": Const.GATEWAY_ID,
                "Temp": 0,
                "Lux": 0,
                "U": 0,
                "I": 0,
                "Cos": 0,
                "P": 0,
                "Minute": 0,
                "KWH": 0,
                "ActiveTime": 0,
                "Scene": 0,
                "Ip": "",
                "Status": 0,
                "Relay_1": False,
                "Relay_2": False,
                "Relay_3": False,
                "Relay_4": False,
                "Scene_1": 0,
                "Scene_2": 0,
                "Scene_3": 0,
                "Scene_4": 0,
                "Minute_1": 0,
                "Minute_2": 0,
                "Minute_3": 0,
                "Minute_4": 0,

            })
        if network is None:
            self.__db.Services.NetworkService.InsertNetwork({
                "NetworkId": Const.RIIM_NETWORK_ID,
                "GatewayMac": ''.join(re.findall('..', '%012x' % uuid.getnode())),
                "FirmwareVersion": Const.FIRMWARE_FIRST_VERSION,
                "NetworkKey": "000102030405060708090a0b0c0d0e0f",
                "TXPower": 0
            })

    def send_devices_status(self) -> dict:
        with threading.Lock():
            rel = self.__db.Services.DeviceService.FindAllDevice()
        devices = rel.fetchall()

        with threading.Lock():
            rel2 = self.__db.Services.DevicePropertyService.FindAllDevicePropertyMapping()
        devices_property_mapping = rel2.fetchall()

        with threading.Lock():
            rel3 = self.__db.Services.GatewayService.FindGatewayById(
                Const.GATEWAY_ID)
        gateway = dict(rel3.fetchone())

        devices_address = []

        res = {
            "RQI": str(uuid.uuid4()),
            "TYPCMD": "DeviceStatus",
            "Gateway": {
                "Temp": gateway.get("Temp"),
                "Lux": gateway.get("Lux"),
                "U": gateway.get("U"),
                "I": gateway.get("I"),
                "Cos": gateway.get("Cos"),
                "P": gateway.get("P"),
                "Minute": gateway.get("Minute"),
                "KWh": gateway.get("KWH"),
                "Status": gateway.get("Status")
            },
            "Devices": []
        }

        temp = {}

        if len(devices) != 0:
            for device in devices:
                # added by cungdd
                isOnline = False
                if time.time() - device['UpdateTime'] <= Const.HC_CHECK_DEVICE_ONLINE_STATUS_INTERVAL:
                    isOnline = True

                devices_address.append(device["DeviceAddress"])
                temp[device["DeviceAddress"]] = {
                    "Device": device["DeviceAddress"],
                    "Online": isOnline,
                    "Status": 0,
                    "Scene": device['SceneCurrent'],
                    "Relay": device['RelayCurrent'],
                    "DIM": device['DimCurrent'],
                    "Temp": device['TCurrent'],
                    "Lux": device['LuxCurrent'],
                    "U": device['VCurrent'],
                    "I": device['ICurrent'],
                    "Cos": device['CosCurrent'],
                    "P": device['PCurrent'],
                    "KWh": device['KWhCurrent']
                }

        if len(devices_property_mapping) != 0:
            for devicePropertyMapping in devices_property_mapping:
                r = devicePropertyMapping
                if r["PropertyId"] == Const.PROPERTY_RELAY_ID:
                    if r["PropertyValue"] == 0:
                        temp[r["DeviceAddress"]]["Relay"] = False
                    if r["PropertyValue"] == 1:
                        temp[r["DeviceAddress"]]["Relay"] = True
                    continue
                if r["PropertyId"] == Const.PROPERTY_DIM_ID:
                    temp[r["DeviceAddress"]]["DIM"] = int(r["PropertyValue"])
                    continue
                if r["PropertyId"] == Const.PROPERTY_P_ID:
                    temp[r["DeviceAddress"]]["P"] = r["PropertyValue"]
                    continue
                if r["PropertyId"] == Const.PROPERTY_TEMP_ID:
                    temp[r["DeviceAddress"]]["Temp"] = r["PropertyValue"]
                    continue
                if r["PropertyId"] == Const.PROPERTY_LUX_ID:
                    temp[r["DeviceAddress"]]["Lux"] = r["PropertyValue"]
                    continue
                if r["PropertyId"] == Const.PROPERTY_U_ID:
                    temp[r["DeviceAddress"]]["U"] = r["PropertyValue"]
                    continue
                if r["PropertyId"] == Const.PROPERTY_I_ID:
                    temp[r["DeviceAddress"]]["I"] = r["PropertyValue"]
                    continue
                if r["PropertyId"] == Const.PROPERTY_COS_ID:
                    temp[r["DeviceAddress"]]["Cos"] = r["PropertyValue"]
                    continue
                if r["PropertyId"] == Const.PROPERTY_KWH_ID:
                    temp[r["DeviceAddress"]]["KWh"] = r["PropertyValue"]
                    continue

        with threading.Lock():
            rel4 = self.__db.Services.EventTriggerOutputDeviceMappingService.FindEventTriggerOutputDeviceMappingByCondition(
                self.__db.Table.EventTriggerOutputDeviceMappingTable.c.DeviceAddress.in_(
                    devices_address)
            )
        scenes = rel4.fetchall()

        if len(scenes) != 0:
            for scene in scenes:
                temp[scene["DeviceAddress"]]["Scene"] = scene["EventTriggerId"]
        for t in temp:
            res["Devices"].append(temp[t])
        with threading.Lock():
            self.__globalVariables.mqtt_need_response_dict[res["RQI"]] = res
        return res

    def report_network_info(self) -> dict:
        rel = self.__db.Services.NetworkService.FindNetworkById(
            Const.RIIM_NETWORK_ID)
        network = rel.fetchone()
        res = {}
        if network is None:
            res = {
                "RQI": str(uuid.uuid4()),
                "TYPCMD": "NetInfor",
                "NETKEY": None,
                "TXPower": None,
                "MAC": None,
                "FirmVer": None
            }
        if network is not None:
            res = {
                "RQI": str(uuid.uuid4()),
                "TYPCMD": "NetInfor",
                "NETKEY": network["NetworkKey"],
                "TXPower": network["TXPower"],
                "MAC": network["GatewayMac"],
                "FirmVer": network["FirmwareVersion"]
            }
        with threading.Lock():
            self.__globalVariables.mqtt_need_response_dict[res["RQI"]] = res
        return res

    def update_devices_online_status_to_global_dict(self):
        with threading.Lock():
            devices = self.__db.Services.DeviceService.FindAllDevice()
        if devices is None:
            return
        for device in devices:
            device_address = device['DeviceAddress']
            device_online_status = device['IsOnline']
            with threading.Lock():
                self.__globalVariables.devices_online_status_dict[device_address] = device_online_status

    def load_devices_heartbeat_to_global_dict(self):
        with threading.Lock():
            devices = self.__db.Services.DeviceService.FindAllDevice()
        if devices:
            return
        for device in devices:
            device_address = device['DeviceAddress']
            device_heartbeat_waiting_count = 0
            with threading.Lock():
                self.__globalVariables.devices_heartbeat_dict[
                    device_address] = device_heartbeat_waiting_count

    def update_device_online_status_to_db(self, device_address: str, is_online: bool):
        with threading.Lock():
            self.__db.Services.DeviceService.UpdateDeviceByCondition(
                self.__db.Table.DeviceTable.c.DeviceAddress == device_address, {"IsOnline": is_online})
