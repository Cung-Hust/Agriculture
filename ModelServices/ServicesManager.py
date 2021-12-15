from Table.TableManager import TableManager
from sqlalchemy.engine.base import Connection
from ModelServices.DeviceServices import DeviceServices
from ModelServices.NetworkServices import NetworkServices
from ModelServices.GroupServices import GroupServices
from ModelServices.GroupDeviceMappingServices import GroupDeviceMappingServices
from ModelServices.GatewayServices import GatewayServices
from ModelServices.GatewayEventTriggerServices import GatewayEventTriggerServices
from ModelServices.GatewayEventTriggerOutputRelayServices import GatewayEventTriggerOutputRelayServices
from ModelServices.EventTriggerServices import EventTriggerServices
from ModelServices.EventTriggerInputDeviceMappingServices import EventTriggerInputDeviceMappingServices
from ModelServices.EventTriggerInputDeviceSetupValueServices import EventTriggerInputDeviceSetupValueServices
from ModelServices.EventTriggerOutputDeviceMappingServices import EventTriggerOutputDeviceMappingServices
from ModelServices.EventTriggerOutputDeviceSetupValueServices import EventTriggerOutputDeviceSetupValueServices
from ModelServices.EventTriggerOutputGroupMappingServices import EventTriggerOutputGroupMappingServices
from ModelServices.EventTriggerOutputGroupSetupValueServices import EventTriggerOutputGroupSetupValueServices
from ModelServices.DevicePropertyMappingServices import DevicePropertyMappingServices


class MetaService(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaService, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ServicesManager(metaclass=MetaService):
    def __init__(self, table: TableManager, context: Connection):
        self.__deviceService = DeviceServices(table.DeviceTable, context)
        self.__networkService = NetworkServices(table.NetworkTable, context)
        self.__groupService = GroupServices(table.GroupTable, context)
        self.__groupDeviceMappingService = GroupDeviceMappingServices(table.GroupDeviceMappingTable, context)
        self.__gatewayService = GatewayServices(table.GatewayTable, context)
        self.__eventTriggerService = EventTriggerServices(table.EventTriggerTable, context)
        self.__gatewayEventTriggerService = GatewayEventTriggerServices(table.GatewayEventTriggerTable, context)
        self.__gatewayEventTriggerOutputRelayService = GatewayEventTriggerOutputRelayServices(
            table.GatewayEventTriggerOutputRelayTable, context)
        self.__eventTriggerInputDeviceMappingService = EventTriggerInputDeviceMappingServices(
            table.EventTriggerInputDeviceMappingTable, context)
        self.__eventTriggerInputDeviceSetupValueService = EventTriggerInputDeviceSetupValueServices(
            table.EventTriggerInputDeviceSetupValueTable, context
        )
        self.__eventTriggerOutputDeviceMappingService = EventTriggerOutputDeviceMappingServices(
            table.EventTriggerOutputDeviceMappingTable, context
        )
        self.__eventTriggerOutputDeviceSetupValueService = EventTriggerOutputDeviceSetupValueServices(
            table.EventTriggerOutputDeviceSetupValueTable, context
        )
        self.__eventTriggerOutputGroupMappingService = EventTriggerOutputGroupMappingServices(
            table.EventTriggerOutputGroupMappingTable, context
        )
        self.__eventTriggerOutputGroupSetupValueService = EventTriggerOutputGroupSetupValueServices(
            table.EventTriggerOutputGroupSetupValueTable, context
        )
        self.__devicePropertyMappingService = DevicePropertyMappingServices(
            table.DevicePropertyMappingTable, context
        )

    @property
    def DeviceService(self):
        return self.__deviceService

    @property
    def NetworkService(self):
        return self.__networkService

    @property
    def GroupService(self):
        return self.__groupService

    @property
    def GroupDeviceMappingService(self):
        return self.__groupDeviceMappingService

    @property
    def GatewayService(self):
        return self.__gatewayService

    @property
    def GatewayEventTriggerOutputRelayService(self):
        return self.__gatewayEventTriggerOutputRelayService

    @property
    def EventTriggerService(self):
        return self.__eventTriggerService

    @property
    def GatewayEventTriggerService(self):
        return self.__gatewayEventTriggerService

    @property
    def EventTriggerInputDeviceMappingService(self):
        return self.__eventTriggerInputDeviceMappingService

    @property
    def EventTriggerInputDeviceSetupValueService(self):
        return self.__eventTriggerInputDeviceSetupValueService

    @property
    def EventTriggerOutputDeviceMappingService(self):
        return self.__eventTriggerOutputDeviceMappingService
    
    @property
    def EventTriggerOutputDeviceSetupValueService(self):
        return self.__eventTriggerOutputDeviceSetupValueService
    
    @property
    def EventTriggerOutputGroupMappingService(self):
        return self.__eventTriggerOutputGroupMappingService
    
    @property
    def EventTriggerOutputGroupSetupValueService(self):
        return self.__eventTriggerOutputGroupSetupValueService

    @property
    def DevicePropertyService(self):
        return self.__devicePropertyMappingService
