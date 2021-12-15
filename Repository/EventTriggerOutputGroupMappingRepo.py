from sqlalchemy import Table
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.engine.base import Connection


class EventTriggerOutputGroupMappingRepo:
    __eventTriggerOutputGroupMappingTable: Table
    __context: Connection

    def __init__(self, EventTriggerOutputGroupMappingTable: Table, context: Connection):
        self.__eventTriggerOutputGroupMappingTable = EventTriggerOutputGroupMappingTable
        self.__context = context

    def FindByCondition(self, condition: BinaryExpression):
        ins = self.__eventTriggerOutputGroupMappingTable.select().where(condition)
        rel = self.__context.execute(ins)
        return rel

    def UpdateByCondition(self, condition: BinaryExpression, values: dict):
        ins = self.__eventTriggerOutputGroupMappingTable.update().where(condition).values(values)
        self.__context.execute(ins)

    def Insert(self, values: dict):
        ins = self.__eventTriggerOutputGroupMappingTable.insert()
        self.__context.execute(ins, values)

    def InsertMany(self, values: list):
        ins = self.__eventTriggerOutputGroupMappingTable.insert()
        self.__context.execute(ins, values)

    def RemoveByCondition(self, condition: BinaryExpression):
        ins = self.__eventTriggerOutputGroupMappingTable.delete().where(condition)
        self.__context.execute(ins)
