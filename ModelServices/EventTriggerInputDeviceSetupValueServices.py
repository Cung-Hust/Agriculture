from Repository.EventTriggerInputDeviceSetupValueRepo import EventTriggerInputDeviceSetupValueRepo
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql.expression import BinaryExpression


class MetaEventTriggerInputDeviceSetupValueServices(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaEventTriggerInputDeviceSetupValueServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class EventTriggerInputDeviceSetupValueServices(metaclass=MetaEventTriggerInputDeviceSetupValueServices):
    __eventTriggerInputDeviceSetupValueRepo: EventTriggerInputDeviceSetupValueRepo

    def __init__(self, EventTriggerInputDeviceSetupValueTable: Table, context: Connection):
        self.__eventTriggerInputDeviceSetupValueRepo = EventTriggerInputDeviceSetupValueRepo(
            EventTriggerInputDeviceSetupValueTable, context)

    def FindEventTriggerIInputDeviceSetupValueByCondition(self, condition: BinaryExpression):
        rel = self.__eventTriggerInputDeviceSetupValueRepo.FindByCondition(condition)
        return rel

    def UpdateEventTriggerInputDeviceSetupValueByCondition(self, condition: BinaryExpression, values: dict):
        self.__eventTriggerInputDeviceSetupValueRepo.UpdateByCondition(condition, values)

    def InsertEventTriggerInputDeviceSetupValue(self, values: dict):
        self.__eventTriggerInputDeviceSetupValueRepo.Insert(values)

    def InsertManyEventTriggerInputDeviceSetupValue(self, values: list):
        self.__eventTriggerInputDeviceSetupValueRepo.InsertMany(values)

    def RemoveEventTriggerInputDeviceSetupValueByCondition(self, condition: BinaryExpression):
        self.__eventTriggerInputDeviceSetupValueRepo.RemoveByCondition(condition)