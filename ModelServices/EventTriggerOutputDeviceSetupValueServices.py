from Repository.EventTriggerOutputDeviceSetupValueRepo import EventTriggerOutputDeviceSetupValueRepo
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql.expression import BinaryExpression


class MetaEventTriggerOutputDeviceSetupValueServices(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaEventTriggerOutputDeviceSetupValueServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class EventTriggerOutputDeviceSetupValueServices(metaclass=MetaEventTriggerOutputDeviceSetupValueServices):
    __eventTriggerOutputDeviceSetupValueRepo: EventTriggerOutputDeviceSetupValueRepo

    def __init__(self, EventTriggerOutputDeviceSetupValueTable: Table, context: Connection):
        self.__eventTriggerOutputDeviceSetupValueRepo = EventTriggerOutputDeviceSetupValueRepo(EventTriggerOutputDeviceSetupValueTable, context)

    def FindEventTriggerOutputDeviceSetupValueByCondition(self, condition: BinaryExpression):
        rel = self.__eventTriggerOutputDeviceSetupValueRepo.FindByCondition(condition)
        return rel

    def UpdateEventTriggerOutputDeviceSetupValueByCondition(self, condition: BinaryExpression, values: dict):
        self.__eventTriggerOutputDeviceSetupValueRepo.UpdateByCondition(condition, values)

    def InsertEventTriggerOutputDeviceSetupValue(self, values: dict):
        self.__eventTriggerOutputDeviceSetupValueRepo.Insert(values)

    def InsertManyEventTriggerOutputDeviceSetupValue(self, values: list):
        self.__eventTriggerOutputDeviceSetupValueRepo.InsertMany(values)

    def RemoveEventTriggerOutputDeviceSetupValueByCondition(self, condition: BinaryExpression):
        self.__eventTriggerOutputDeviceSetupValueRepo.RemoveByCondition(condition)