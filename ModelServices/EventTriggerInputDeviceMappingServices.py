from Repository.EventTriggerInputDeviceMappingRepo import EventTriggerInputDeviceMappingRepo
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql.expression import BinaryExpression


class MetaEventTriggerInputDeviceMappingServices(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaEventTriggerInputDeviceMappingServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class EventTriggerInputDeviceMappingServices(metaclass=MetaEventTriggerInputDeviceMappingServices):
    __eventTriggerInputDeviceMappingRepo: EventTriggerInputDeviceMappingRepo

    def __init__(self, EventTriggerInputDeviceMappingTable: Table, context: Connection):
        self.__eventTriggerInputDeviceMappingRepo = EventTriggerInputDeviceMappingRepo(EventTriggerInputDeviceMappingTable, context)

    def FindEventTriggerInputDeviceMappingByCondition(self, condition: BinaryExpression):
        rel = self.__eventTriggerInputDeviceMappingRepo.FindByCondition(condition)
        return rel

    def UpdateEventTriggerInputDeviceMappingByCondition(self, condition: BinaryExpression, values: dict):
        self.__eventTriggerInputDeviceMappingRepo.UpdateByCondition(condition, values)

    def InsertEventTriggerInputDeviceMapping(self, values: dict):
        self.__eventTriggerInputDeviceMappingRepo.Insert(values)

    def InsertManyEventTriggerInputDeviceMapping(self, values: list):
        self.__eventTriggerInputDeviceMappingRepo.InsertMany(values)

    def RemoveEventTriggerInputDeviceMappingByCondition(self, condition: BinaryExpression):
        self.__eventTriggerInputDeviceMappingRepo.RemoveByCondition(condition)