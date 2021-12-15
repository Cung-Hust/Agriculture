from Repository.EventTriggerOutputGroupMappingRepo import EventTriggerOutputGroupMappingRepo
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql.expression import BinaryExpression


class MetaEventTriggerOutputGroupMappingServices(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaEventTriggerOutputGroupMappingServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class EventTriggerOutputGroupMappingServices(metaclass=MetaEventTriggerOutputGroupMappingServices):
    __eventTriggerOutputGroupMappingRepo: EventTriggerOutputGroupMappingRepo

    def __init__(self, EventTriggerOutputGroupMappingTable: Table, context: Connection):
        self.__eventTriggerOutputGroupMappingRepo = EventTriggerOutputGroupMappingRepo(
            EventTriggerOutputGroupMappingTable, context)

    def FindEventTriggerOutputGroupMappingByCondition(self, condition: BinaryExpression):
        rel = self.__eventTriggerOutputGroupMappingRepo.FindByCondition(condition)
        return rel

    def UpdateEventTriggerOutputGroupMappingByCondition(self, condition: BinaryExpression, values: dict):
        self.__eventTriggerOutputGroupMappingRepo.UpdateByCondition(condition, values)

    def InsertEventTriggerOutputGroupMapping(self, values: dict):
        self.__eventTriggerOutputGroupMappingRepo.Insert(values)

    def InsertManyEventTriggerOutputGroupMapping(self, values: list):
        self.__eventTriggerOutputGroupMappingRepo.InsertMany(values)

    def RemoveEventTriggerOutputGroupMappingByCondition(self, condition: BinaryExpression):
        self.__eventTriggerOutputGroupMappingRepo.RemoveByCondition(condition)