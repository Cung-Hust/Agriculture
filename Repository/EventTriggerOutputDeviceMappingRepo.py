from sqlalchemy import Table
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.engine.base import Connection


class EventTriggerOutputDeviceMappingRepo:
    __eventTriggerOutputDeviceMappingTable: Table
    __context: Connection

    def __init__(self, EventTriggerOutputDeviceMappingTable: Table, context: Connection):
        self.__eventTriggerOutputDeviceMappingTable = EventTriggerOutputDeviceMappingTable
        self.__context = context

    def FindByCondition(self, condition: BinaryExpression):
        ins = self.__eventTriggerOutputDeviceMappingTable.select().where(condition)
        rel = self.__context.execute(ins)
        return rel

    def UpdateByCondition(self, condition: BinaryExpression, values: dict):
        ins = self.__eventTriggerOutputDeviceMappingTable.update().where(condition).values(values)
        self.__context.execute(ins)

    def Insert(self, values: dict):
        ins = self.__eventTriggerOutputDeviceMappingTable.insert()
        self.__context.execute(ins, values)

    def InsertMany(self, values: list):
        ins = self.__eventTriggerOutputDeviceMappingTable.insert()
        self.__context.execute(ins, values)

    def RemoveByCondition(self, condition: BinaryExpression):
        ins = self.__eventTriggerOutputDeviceMappingTable.delete().where(condition)
        self.__context.execute(ins)
