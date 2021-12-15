from Repository.EventTriggerOutputDeviceMappingRepo import EventTriggerOutputDeviceMappingRepo
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql.expression import BinaryExpression


class MetaEventTriggerOutputDeviceMappingServices(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaEventTriggerOutputDeviceMappingServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class EventTriggerOutputDeviceMappingServices(metaclass=MetaEventTriggerOutputDeviceMappingServices):
    __eventTriggerOutputDeviceMappingRepo: EventTriggerOutputDeviceMappingRepo

    def __init__(self, EventTriggerOutputDeviceMappingTable: Table, context: Connection):
        self.__eventTriggerOutputDeviceMappingRepo = EventTriggerOutputDeviceMappingRepo(
            EventTriggerOutputDeviceMappingTable, context)

    def FindEventTriggerOutputDeviceMappingByCondition(self, condition: BinaryExpression):
        rel = self.__eventTriggerOutputDeviceMappingRepo.FindByCondition(condition)
        return rel

    def UpdateEventTriggerOutputDeviceMappingByCondition(self, condition: BinaryExpression, values: dict):
        self.__eventTriggerOutputDeviceMappingRepo.UpdateByCondition(condition, values)

    def InsertEventTriggerOutputDeviceMapping(self, values: dict):
        self.__eventTriggerOutputDeviceMappingRepo.Insert(values)

    def InsertManyEventTriggerOutputDeviceMapping(self, values: list):
        self.__eventTriggerOutputDeviceMappingRepo.InsertMany(values)

    def RemoveEventTriggerOutputDeviceMappingByCondition(self, condition: BinaryExpression):
        self.__eventTriggerOutputDeviceMappingRepo.RemoveByCondition(condition)