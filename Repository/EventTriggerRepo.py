from sqlalchemy import Table
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.engine.base import Connection


class EventTriggerRepo:
    __eventTriggerTable: Table
    __context: Connection

    def __init__(self, EventTriggerTable: Table, context: Connection):
        self.__eventTriggerTable = EventTriggerTable
        self.__context = context

    def FindById(self, Id: int):
        ins = self.__eventTriggerTable.select().where(self.__eventTriggerTable.c.EventTriggerId == Id)
        rel = self.__context.execute(ins)
        return rel

    def UpdateByCondition(self, condition: BinaryExpression, values: dict):
        ins = self.__eventTriggerTable.update().where(condition).values(values)
        self.__context.execute(ins)

    def Insert(self, values: dict):
        ins = self.__eventTriggerTable.insert()
        self.__context.execute(ins, values)

    def RemoveByCondition(self, condition: BinaryExpression):
        ins = self.__eventTriggerTable.delete().where(condition)
        self.__context.execute(ins)
