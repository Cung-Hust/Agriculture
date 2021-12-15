from Handler.MqttTypCmdHandlers.ConfigGWRFHandler import ConfigGWRFHandler
from Handler.MqttTypCmdHandlers.DelDevHandler import DelDevHandler
from Handler.MqttTypCmdHandlers.ActiveSceneHandler import ActiveSceneHandler
from Handler.MqttTypCmdHandlers.ConfigDevHandler import ConfigDevHandler
from Handler.MqttTypCmdHandlers.ControlDeviceHandler import ControlDeviceHandler
from Handler.MqttTypCmdHandlers.ControlRelayHandler import ControlRelayHandler
from Handler.MqttTypCmdHandlers.CreateGroupHandler import CreateGroupHandler
from Handler.MqttTypCmdHandlers.DelDevFrGroupHandler import DelDevFrGroupHandler
from Handler.MqttTypCmdHandlers.DelDeviceInSceneHandler import DelDeviceInSceneHandler
from Handler.MqttTypCmdHandlers.DelGroupHandler import DelGroupHandler
from Handler.MqttTypCmdHandlers.DelSceneHandler import DelSceneHandler
from Handler.MqttTypCmdHandlers.DeviceCommanderHandler import DeviceCommanderHandler
from Handler.MqttTypCmdHandlers.DeviceFirmURLHandler import DeviceFirmURLHandler
from Handler.MqttTypCmdHandlers.GatewayCommanderHandler import GatewayCommanderHandler
from Handler.MqttTypCmdHandlers.GatewayFirmURLHandler import GatewayFirmURLHandler
from Handler.MqttTypCmdHandlers.GetGatewayInforHandler import GetGatewayInForHandler
from Handler.MqttTypCmdHandlers.PingDeviceHandler import PingDeviceHandler
from Handler.MqttTypCmdHandlers.PingGatewayHandler import PingGatewayHandler
from Handler.MqttTypCmdHandlers.RebootDeviceHandler import RebootDeviceHandler
from Handler.MqttTypCmdHandlers.RebootGatewayHandler import RebootGatewayHandler
from Handler.MqttTypCmdHandlers.RequestInforHandler import RequestInforHandler
from Handler.MqttTypCmdHandlers.SetSceneHandler import SetSceneHandler
from Handler.MqttTypCmdHandlers.StopSceneHandler import StopSceneHandler
from Handler.MqttTypCmdHandlers.AddDeviceHandler import AddDeviceHandler
from Handler.MqttTypCmdHandlers.SetGwSceneHandler import SetGwSceneHandler
from Handler.MqttTypCmdHandlers.StopGwSceneHandler import StopGwSceneHandler
from Handler.MqttTypCmdHandlers.DelGwSceneHandler import DelGwSceneHandler
from Handler.MqttTypCmdHandlers.ActiveGwSceneHandler import ActiveGwSceneHandler

from Constracts import ITransport
import logging


class TypeCmdHandlerManager:
    def __init__(self, log: logging.Logger, mqtt: ITransport, uart: ITransport):
        # self.__activeSceneHandler = ActiveSceneHandler(log, mqtt)
        # self.__configGWRFHandler = ConfigGWRFHandler(log, mqtt)
        # self.__configDevHandler = ConfigDevHandler(log, mqtt)
        self.__controlDeviceHandler = ControlDeviceHandler(log, mqtt, uart)
        # self.__ControlRelayHandler = ControlRelayHandler(log, mqtt)
        # self.__delDevHandler = DelDevHandler(log, mqtt)
        # self.__createGroupHandler = CreateGroupHandler(log, mqtt)
        # self.__delDevFrGroupHandler = DelDevFrGroupHandler(log, mqtt)
        # self.__delDeviceInSceneHandler = DelDeviceInSceneHandler(log, mqtt)
        # self.__delGroupHandler = DelGroupHandler(log, mqtt)
        # self.__delSceneHandler = DelSceneHandler(log, mqtt)
        # self.__deviceCommanderHandler = DeviceCommanderHandler(log, mqtt)
        # self.__deviceFirmURLHandler = DeviceFirmURLHandler(log, mqtt)
        # self.__gatewayCommanderHandler = GatewayCommanderHandler(log, mqtt)
        # self.__gatewayFirmURLHandler = GatewayFirmURLHandler(log, mqtt)
        # self.__getGatewayInforHandler = GetGatewayInForHandler(log, mqtt)
        # self.__pingDeviceHandler = PingDeviceHandler(log, mqtt)
        # self.__pingGatewayHandler = PingGatewayHandler(log, mqtt)
        # self.__rebootDeviceHandler = RebootDeviceHandler(log, mqtt)
        # self.__rebootGatewayHandler = RebootGatewayHandler(log, mqtt)
        # self.__requestInforHandler = RequestInforHandler(log, mqtt)
        # self.__setSceneHandler = SetSceneHandler(log, mqtt)
        # self.__stopSceneHandler = StopSceneHandler(log, mqtt)
        # self.__addDeviceHandler = AddDeviceHandler(log, mqtt)
        # self.__setGwSceneHandler = SetGwSceneHandler(log, mqtt)
        # self.__stopGwSceneHandler = StopGwSceneHandler(log, mqtt)
        # self.__delGwSceneHandler = DelGwSceneHandler(log, mqtt)
        # self.__activeGwSceneHandler = ActiveGwSceneHandler(log, mqtt)

    @property
    def ActiveGwScene(self):
        return self.__activeGwSceneHandler

    @property
    def DelGwScene(self):
        return self.__delGwSceneHandler

    @property
    def StopGwScene(self):
        return self.__stopGwSceneHandler

    @property
    def SetGwScene(self):
        return self.__setGwSceneHandler

    @property
    def ActiveScene(self):
        return self.__activeSceneHandler

    @property
    def ConfigGWRF(self):
        return self.__configGWRFHandler

    @property
    def ConfigDev(self):
        return self.__configDevHandler

    @property
    def ControlDevice(self):
        return self.__controlDeviceHandler

    @property
    def ControlRelay(self):
        return self.__ControlRelayHandler

    @property
    def DelDev(self):
        return self.__delDevHandler

    @property
    def CreateGroup(self):
        return self.__createGroupHandler

    @property
    def DelDevFrGroup(self):
        return self.__delDevFrGroupHandler

    @property
    def DelDeviceInScene(self):
        return self.__delDeviceInSceneHandler

    @property
    def DelGroup(self):
        return self.__delGroupHandler

    @property
    def DelScene(self):
        return self.__delSceneHandler

    @property
    def DeviceCommander(self):
        return self.__deviceCommanderHandler

    @property
    def DeviceFirmURL(self):
        return self.__deviceFirmURLHandler

    @property
    def GatewayCommander(self):
        return self.__gatewayCommanderHandler

    @property
    def GatewayFirmURL(self):
        return self.__gatewayFirmURLHandler

    @property
    def GetGatewayInfor(self):
        return self.__getGatewayInforHandler

    @property
    def PingDevice(self):
        return self.__pingDeviceHandler

    @property
    def PingGateway(self):
        return self.__pingGatewayHandler

    @property
    def RebootDevice(self):
        return self.__rebootDeviceHandler

    @property
    def RebootGateway(self):
        return self.__rebootGatewayHandler

    @property
    def RequestInfor(self):
        return self.__requestInforHandler

    @property
    def SetScene(self):
        return self.__setSceneHandler

    @property
    def StopScene(self):
        return self.__stopSceneHandler

    @property
    def AddDevice(self):
        return self.__addDeviceHandler
