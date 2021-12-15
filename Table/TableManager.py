from sqlalchemy import MetaData
from Table.Group import Group
from Table.Device import Device
from Table.EventTriggerInputDeviceMapping import EventTriggerInputDeviceMapping
from Table.EventTriggerInputDeviceSetupValue import EventTriggerInputDeviceSetupValue
from Table.Network import Network
from Table.Property import Property
from Table.Schedule import Schedule
from Table.DevicePropertyMapping import DevicePropertyMapping
from Table.EventTrigger import EventTrigger
from Table.Gateway import Gateway
from Table.EventTriggerOutputDeviceMapping import EventTriggerOutputDeviceMapping
from Table.EventTriggerOutputDeviceSetupValue import EventTriggerOutputDeviceSetupValue
from Table.EventTriggerOutputGroupMapping import EventTriggerOutputGroupMapping
from Table.EventTriggerOutputGroupSetupValue import EventTriggerOutputGroupSetupValue
from Table.GroupDeviceMapping import GroupDeviceMapping
from Table.DeviceFirmwareUpdate import DeviceFirmwareUpdate
from Table.GatewayFirmwareUpdate import GatewayFirmwareUpdate
from Table.GatewayEventTriggerOutputRelay import GatewayEventTriggerOutputRelay
from Table.GatewayEventTrigger import GatewayEventTrigger
from Table.GatewayEventTriggerInputDeviceMappingSetupValue import GatewayEventTriggerInputDeviceSetupValue
from Table.GatewayEventTriggerInputDeviceMapping import GatewayEventTriggerInputDeviceMapping


class TableManager:
    def __init__(self, metadata: MetaData):
        self.__groupTable = Group(metadata)
        self.__deviceTable = Device(metadata)
        self.__eventTriggerInputDeviceMappingTable = EventTriggerInputDeviceMapping(metadata)
        self.__eventTriggerInputDeviceSetupValueTable = EventTriggerInputDeviceSetupValue(metadata)
        self.__networkTable = Network(metadata)
        self.__propertyTable = Property(metadata)
        self.__scheduleTable = Schedule(metadata)
        self.__devicePropertyMappingTable = DevicePropertyMapping(metadata)
        self.__eventTriggerTable = EventTrigger(metadata)
        self.__gatewayTable = Gateway(metadata)
        self.__eventTriggerOutputDeviceMappingTable = EventTriggerOutputDeviceMapping(metadata)
        self.__eventTriggerOutputDeviceSetupValueTable = EventTriggerOutputDeviceSetupValue(metadata)
        self.__eventTriggerOutputGroupMappingTable = EventTriggerOutputGroupMapping(metadata)
        self.__eventTriggerOutputGroupSetupValueTable = EventTriggerOutputGroupSetupValue(metadata)
        self.__groupDeviceMappingTable = GroupDeviceMapping(metadata)
        self.__deviceFirmwareUpdateTable = DeviceFirmwareUpdate(metadata)
        self.__gatewayFirmwareUpdateTable = GatewayFirmwareUpdate(metadata)
        self.__gatewayEventTriggerOutputRelayTable = GatewayEventTriggerOutputRelay(metadata)
        self.__gatewayEventTriggerInputDeviceMappingTable = GatewayEventTriggerInputDeviceMapping(metadata)
        self.__gatewayEventTriggerInputDeviceSetupValueTable = GatewayEventTriggerInputDeviceSetupValue(metadata)
        self.__gatewayEventTriggerTable = GatewayEventTrigger(metadata)

    @property
    def GatewayEventTriggerInputDeviceMappingTable(self):
        return self.__gatewayEventTriggerInputDeviceMappingTable.gatewayEventTriggerInputDeviceMapping

    @property
    def GatewayEventTriggerInputDeviceSetupValueTable(self):
        return self.__gatewayEventTriggerInputDeviceSetupValueTable.gatewayEventTriggerInputDeviceSetupValue

    @property
    def GatewayEventTriggerTable(self):
        return self.__gatewayEventTriggerTable.gatewayEventTrigger

    @property
    def GroupTable(self):
        return self.__groupTable.group

    @property
    def DeviceTable(self):
        return self.__deviceTable.device

    @property
    def GroupDeviceMappingTable(self):
        return self.__groupDeviceMappingTable.groupDeviceMapping

    @property
    def EventTriggerInputDeviceMappingTable(self):
        return self.__eventTriggerInputDeviceMappingTable.eventTriggerInputDeviceMapping

    @property
    def EventTriggerInputDeviceSetupValueTable(self):
        return self.__eventTriggerInputDeviceSetupValueTable.eventTriggerInputDeviceSetupValue

    @property
    def NetworkTable(self):
        return self.__networkTable.network

    @property
    def PropertyTable(self):
        return self.__propertyTable.property

    @property
    def ScheduleTable(self):
        return self.__scheduleTable.schedule

    @property
    def DevicePropertyMappingTable(self):
        return self.__devicePropertyMappingTable.devicePropertyMapping

    @property
    def EventTriggerTable(self):
        return self.__eventTriggerTable.eventTrigger

    @property
    def GatewayTable(self):
        return self.__gatewayTable.gateway

    @property
    def EventTriggerOutputDeviceMappingTable(self):
        return self.__eventTriggerOutputDeviceMappingTable.eventTriggerOutputDeviceMapping

    @property
    def EventTriggerOutputDeviceSetupValueTable(self):
        return self.__eventTriggerOutputDeviceSetupValueTable.eventTriggerOutputDeviceSetupValue

    @property
    def EventTriggerOutputGroupMappingTable(self):
        return self.__eventTriggerOutputGroupMappingTable.eventTriggerOutputGroupMapping

    @property
    def EventTriggerOutputGroupSetupValueTable(self):
        return self.__eventTriggerOutputGroupSetupValueTable.eventTriggerOutputGroupSetupValue

    @property
    def DeviceFirmwareUpdateTable(self):
        return self.__deviceFirmwareUpdateTable.deviceFirmwareUpdate

    @property
    def GatewayFirmwareUpdateTable(self):
        return self.__gatewayFirmwareUpdateTable.gatewayFirmwareUpdate

    @property
    def GatewayEventTriggerOutputRelayTable(self):
        return self.__gatewayEventTriggerOutputRelayTable.gatewayEventTriggerOutputRelay