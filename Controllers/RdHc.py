import asyncio
import json
import logging
import threading
from Constracts.ITransport import ITransport
from Constracts.IHandler import IHandler
from Helper.System import System
from GlobalVariables.GlobalVariables import GlobalVariables
import Constants.Constant as Const
import uuid
import time


class RdHc:
    __mqttServices: ITransport
    __uartServices: ITransport
    __lock: threading.Lock
    __logger: logging.Logger
    __mqttHandler: IHandler
    __uartHandler: IHandler
    __systemHelper: System
    __globalVariables: GlobalVariables

    def __init__(self, log: logging.Logger, mqtt: ITransport, uart: ITransport,
                 mqtt_handler: IHandler, uart_handler: IHandler):
        self.__logger = log
        self.__mqttServices = mqtt
        self.__uartServices = uart
        self.__lock = threading.Lock()
        self.__mqttHandler = mqtt_handler
        self.__uartHandler = uart_handler
        self.__systemHelper = System(self.__logger)
        self.__globalVariables = GlobalVariables()

    def hc_report_network_info(self):
        print("hc report network info")
        res = self.__systemHelper.report_network_info()
        self.__mqttServices.send(
            Const.MQTT_RESPONSE_TOPIC, json.dumps(res))

    def hc_load_devices_heartbeat_to_global_dict(self):
        self.__systemHelper.load_devices_heartbeat_to_global_dict()

    def hc_add_gateway_event_log(self):
        gateway_event_log = self.__systemHelper.add_gateway_event_log()
        self.__mqttServices.send(
            Const.MQTT_RESPONSE_TOPIC, json.dumps(gateway_event_log))

    def hc_add_basic_info_to_db(self):
        self.__systemHelper.add_basic_info_to_db()

    def hc_update_devices_online_status_to_global_dict(self):
        self.__systemHelper.update_devices_online_status_to_global_dict()

    async def __hc_retry_send_mqtt_mess(self):
        while True:
            if len(self.__globalVariables.mqtt_need_response_dict) > 0:
                with self.__lock:
                    self.__globalVariables.mqtt_need_response_dict.clear()
                await asyncio.sleep(Const.HC_RETRY_SEND_MQTT_MESSAGE_INTERVAL)

    async def __hc_check_heartbeat_and_update_devices_online_status_to_db(self):
        while True:
            for device in self.__globalVariables.devices_heartbeat_dict:
                if self.__globalVariables.devices_heartbeat_dict[device] < 3:
                    self.__globalVariables.devices_heartbeat_dict[device] = \
                        self.__globalVariables.devices_heartbeat_dict[device] + 1
                if self.__globalVariables.devices_heartbeat_dict[device] == 3:
                    if self.__globalVariables.devices_online_status_dict[device]:
                        self.__systemHelper.update_device_online_status_to_db(
                            device_address=device, is_online=False)
            await asyncio.sleep(Const.HC_CHECK_HEARTBEAT_INTERVAL)

    async def __hc_update_devices_online_status_from_db_to_global_dict(self):
        while True:
            self.__systemHelper.update_devices_online_status_to_global_dict()
            await asyncio.sleep(Const.HC_UPDATE_DEVICES_ONLINE_STATUS_TO_GLOBAL_DICT_INTERVAL)

    async def __hc_send_devices_status(self):
        while True:
            print("hc report device state")
            device_state_mes = self.__systemHelper.send_devices_status()
            self.__mqttServices.send(
                Const.MQTT_RESPONSE_TOPIC, json.dumps(device_state_mes))
            await asyncio.sleep(Const.HC_REPORT_DEVICE_STATE_INTERVAL)

    async def __hc_check_connect_with_cloud(self):
        while True:
            print("hc ping to cloud")
            res = {
                "RQI": str(uuid.uuid4()),
                "TYPCMD": "Ping"
            }
            with self.__lock:
                self.__globalVariables.mqtt_need_response_dict[res["RQI"]] = res
            self.__mqttServices.send(
                Const.MQTT_RESPONSE_TOPIC, json.dumps(res))
            await asyncio.sleep(Const.HC_PING_TO_CLOUD_INTERVAL)

    def hc_handler_mqtt_data(self):
        if not self.__mqttServices.receive_data_queue.empty():
            item = self.__mqttServices.receive_data_queue.get()
            print(item)
            self.__mqttHandler.handler(item)
            self.__mqttServices.receive_data_queue.task_done()

    def hc_handler_uart_data(self):
        # print("--> Thread 3 is running")
        if not self.__uartServices.receive_uart_queue.empty():
            item = self.__uartServices.receive_uart_queue.get()
            self.__uartHandler.handler(item)
            self.__uartServices.receive_uart_queue.task_done()

    async def hc_thread_report_interval(self):
        task1 = asyncio.create_task(self.__hc_check_connect_with_cloud())
        task2 = asyncio.create_task(self.__hc_send_devices_status())
        task3 = asyncio.create_task(
            self.__hc_update_devices_online_status_from_db_to_global_dict())
        task4 = asyncio.create_task(
            self.__hc_check_heartbeat_and_update_devices_online_status_to_db())
        tasks = [task1, task2, task3, task4]
        await asyncio.gather(*tasks)
