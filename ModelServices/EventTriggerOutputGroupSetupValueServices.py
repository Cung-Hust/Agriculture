from Repository.EventTriggerOutputGroupSetupValueRepo import EventTriggerOutputGroupSetupValueRepo
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql.expression import BinaryExpression


class MetaEventTriggerOutputGroupSetupValueServices(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaEventTriggerOutputGroupSetupValueServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class EventTriggerOutputGroupSetupValueServices(metaclass=MetaEventTriggerOutputGroupSetupValueServices):
    __eventTriggerOutputGroupSetupValueRepo: EventTriggerOutputGroupSetupValueRepo

    def __init__(self, EventTriggerOutputGroupSetupValueTable: Table, context: Connection):
        self.__eventTriggerOutputGroupSetupValueRepo = EventTriggerOutputGroupSetupValueRepo(
            EventTriggerOutputGroupSetupValueTable, context)

    def FindEventTriggerOutputGroupSetupValueByCondition(self, condition: BinaryExpression):
        rel = self.__eventTriggerOutputGroupSetupValueRepo.FindByCondition(condition)
        return rel

    def UpdateEventTriggerOutputGroupSetupValueByCondition(self, condition: BinaryExpression, values: dict):
        self.__eventTriggerOutputGroupSetupValueRepo.UpdateByCondition(condition, values)

    def InsertEventTriggerOutputGroupSetupValue(self, values: dict):
        self.__eventTriggerOutputGroupSetupValueRepo.Insert(values)

    def InsertManyEventTriggerOutputGroupSetupValue(self, values: list):
        self.__eventTriggerOutputGroupSetupValueRepo.InsertMany(values)

    def RemoveEventTriggerOutputGroupSetupValueByCondition(self, condition: BinaryExpression):
        self.__eventTriggerOutputGroupSetupValueRepo.RemoveByCondition(condition)