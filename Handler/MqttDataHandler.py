import json
import logging
import threading

import Constants.Constant as Const
from Constracts.IHandler import IHandler
from Constracts.ITransport import ITransport
from Handler.MqttTypCmdHandlers.TypeCmdHandlerManager import TypeCmdHandlerManager


class MqttDataHandler(IHandler):
    __logger: logging.Logger
    __mqtt: ITransport
    __uart: ITransport
    __mqttTypeCmdHandlerManager: TypeCmdHandlerManager

    def __init__(self, log: logging.Logger, mqtt: ITransport, uart: ITransport):
        self.__logger = log
        self.__mqtt = mqtt
        self.__uart = uart
        self.__mqttTypeCmdHandlerManager = TypeCmdHandlerManager(
            log, mqtt, uart)

    def handler(self, item):
        topic = item['topic']
        message = item['msg']
        # print(topic, message)
        # switcher = {
        #     Const.MQTT_CONTROL_TOPIC: self.__handler_control_topic,
        #     Const.MQTT_DEVICE_TO_CLOUD_REQUEST_TOPIC: self.__handler_cloud_to_device_request_topic,
        # }
        # func = switcher.get(topic)
        # func(message)
        if topic == Const.MQTT_RESPONSE_TOPIC:
            self.__handler_response_cmd(message)
        else:
            self.__handler_control_cmd(message)
        return

    # def __handler_control_cmd(self, data):
    #     data = json.loads(data)
    #     method = data['method']
    #     params = data['params']
    #     if params == True:
    #         cw = [0x00, 0x05, 0x02, 0x00, 0x01, 0x0D, 0x0A]
    #         self.__uart.send("device", cw)
    #     else:
    #         cw = [0x00, 0x05, 0x02, 0x00, 0x00, 0x0D, 0x0A]
    #         self.__uart.send("device", cw)

    def __handler_control_cmd(self, data):
        try:
            data = json.loads(data)
            method = data['method']
            type_cmd = method[:method.find('_')]
            switcher = {
                "CtrlDev": self.__mqttTypeCmdHandlerManager.ControlDevice.handler,
                # "ConfigGWRF": self.__mqttTypeCmdHandlerManager.ConfigGWRF.handler,
                # "DelDev": self.__mqttTypeCmdHandlerManager.DelDev.handler,
                # "GetGatewayInfor": self.__mqttTypeCmdHandlerManager.GetGatewayInfor.handler,
                # "PingDevice": self.__mqttTypeCmdHandlerManager.PingDevice.handler,
                # "PingGateway": self.__mqttTypeCmdHandlerManager.PingGateway.handler,
                # "RequestInfor": self.__mqttTypeCmdHandlerManager.RequestInfor.handler,
                # "CreateGroup": self.__mqttTypeCmdHandlerManager.CreateGroup.handler,
                # "DelDevFrGroup": self.__mqttTypeCmdHandlerManager.DelDevFrGroup.handler,
                # "DelGroup": self.__mqttTypeCmdHandlerManager.DelGroup.handler,
                # "RebootGateway": self.__mqttTypeCmdHandlerManager.RebootGateway.handler,
                # "RebootDevice": self.__mqttTypeCmdHandlerManager.RebootDevice.handler,
                # "GatewayCommander": self.__mqttTypeCmdHandlerManager.GatewayCommander.handler,
                # "DeviceCommander": self.__mqttTypeCmdHandlerManager.DeviceCommander.handler,
                # "ConfigDev": self.__mqttTypeCmdHandlerManager.ConfigDev.handler,
                # "SetDevScene": self.__mqttTypeCmdHandlerManager.SetScene.handler,
                # "DelDevScene": self.__mqttTypeCmdHandlerManager.DelScene.handler,
                # "DelDeviceInScene": self.__mqttTypeCmdHandlerManager.DelDeviceInScene.handler,
                # "ControlRelay": self.__mqttTypeCmdHandlerManager.ControlRelay.handler,
                # "ActiveDevScene": self.__mqttTypeCmdHandlerManager.ActiveScene.handler,
                # "StopDevScene": self.__mqttTypeCmdHandlerManager.StopScene.handler,
                # "DeviceFirmURL": self.__mqttTypeCmdHandlerManager.DeviceFirmURL.handler,
                # "GatewayFirmURL": self.__mqttTypeCmdHandlerManager.GatewayFirmURL.handler,
                # "AddDevice": self.__mqttTypeCmdHandlerManager.AddDevice.handler,
                # "SetGWScene": self.__mqttTypeCmdHandlerManager.SetGwScene.handler,
                # "DelGWScene": self.__mqttTypeCmdHandlerManager.DelGwScene.handler,
                # "ActiveGWScene": self.__mqttTypeCmdHandlerManager.ActiveGwScene.handler,
                # "StopGWScene": self.__mqttTypeCmdHandlerManager.StopGwScene.handler,
            }

            func = switcher.get(type_cmd)
            func(data)

        except:
            self.__logger.error(
                f"mqtt data receiver in topic {Const.MQTT_CONTROL_TOPIC} invalid")
            print(
                f"mqtt data receiver in topic {Const.MQTT_CONTROL_TOPIC} invalid")

    def __handler_response_cmd(self, data):
        try:
            json_data = json.loads(data)
            rqi = json_data.get("RQI")
            with threading.Lock():
                self.globalVariable.mqtt_need_response_dict.pop(rqi)
        except:
            self.__logger.error(
                f"mqtt data receiver in topic {Const.MQTT_RESPONSE_TOPIC} invalid")
            print(
                f"mqtt data receiver in topic {Const.MQTT_RESPONSE_TOPIC} invalid")
