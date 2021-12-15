from sqlalchemy import Table
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.engine.base import Connection


class EventTriggerInputDeviceMappingRepo:
    __eventTriggerInputDeviceMappingTable: Table
    __context: Connection

    def __init__(self, EventTriggerInputDeviceMappingTable: Table, context: Connection):
        self.__eventTriggerInputDeviceMappingTable = EventTriggerInputDeviceMappingTable
        self.__context = context

    def FindByCondition(self, condition: BinaryExpression):
        ins = self.__eventTriggerInputDeviceMappingTable.select().where(condition)
        rel = self.__context.execute(ins)
        return rel

    def UpdateByCondition(self, condition: BinaryExpression, values: dict):
        ins = self.__eventTriggerInputDeviceMappingTable.update().where(condition).values(values)
        self.__context.execute(ins)

    def Insert(self, values: dict):
        ins = self.__eventTriggerInputDeviceMappingTable.insert()
        self.__context.execute(ins, values)

    def InsertMany(self, values: list):
        ins = self.__eventTriggerInputDeviceMappingTable.insert()
        self.__context.execute(ins, values)

    def RemoveByCondition(self, condition: BinaryExpression):
        ins = self.__eventTriggerInputDeviceMappingTable.delete().where(condition)
        self.__context.execute(ins)
