from Repository.EventTriggerRepo import EventTriggerRepo
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql.expression import BinaryExpression


class MetaEventTriggerServices(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaEventTriggerServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class EventTriggerServices(metaclass=MetaEventTriggerServices):
    __eventTriggerRepo: EventTriggerRepo

    def __init__(self, EventTriggerTable: Table, context: Connection):
        self.__eventTriggerRepo = EventTriggerRepo(EventTriggerTable, context)

    def FindEventTriggerById(self, Id: int):
        rel = self.__eventTriggerRepo.FindById(Id)
        return rel

    def UpdateEventTriggerCondition(self, condition: BinaryExpression, values: dict):
        self.__eventTriggerRepo.UpdateByCondition(condition, values)

    def InsertEventTrigger(self, values: dict):
        self.__eventTriggerRepo.Insert(values)

    def RemoveEventTriggerByCondition(self, condition: BinaryExpression):
        self.__eventTriggerRepo.RemoveByCondition(condition)