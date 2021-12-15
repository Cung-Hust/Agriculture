from sqlalchemy import Table
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.engine.base import Connection


class EventTriggerOutputGroupSetupValueRepo:
    __eventTriggerOutputGroupSetupValueTable: Table
    __context: Connection

    def __init__(self, EventTriggerOutputGroupSetupValueTable: Table, context: Connection):
        self.__eventTriggerOutputGroupSetupValueTable = EventTriggerOutputGroupSetupValueTable
        self.__context = context

    def FindByCondition(self, condition: BinaryExpression):
        ins = self.__eventTriggerOutputGroupSetupValueTable.select().where(condition)
        rel = self.__context.execute(ins)
        return rel

    def UpdateByCondition(self, condition: BinaryExpression, values: dict):
        ins = self.__eventTriggerOutputGroupSetupValueTable.update().where(condition).values(values)
        self.__context.execute(ins)

    def Insert(self, values: dict):
        ins = self.__eventTriggerOutputGroupSetupValueTable.insert()
        self.__context.execute(ins, values)

    def InsertMany(self, values: list):
        ins = self.__eventTriggerOutputGroupSetupValueTable.insert()
        self.__context.execute(ins, values)

    def RemoveByCondition(self, condition: BinaryExpression):
        ins = self.__eventTriggerOutputGroupSetupValueTable.delete().where(condition)
        self.__context.execute(ins)
