from sqlalchemy import Table
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.engine.base import Connection


class EventTriggerInputDeviceSetupValueRepo:
    __eventTriggerInputDeviceSetupValueTable: Table
    __context: Connection

    def __init__(self, EventTriggerInputDeviceSetupValueTable: Table, context: Connection):
        self.__eventTriggerInputDeviceSetupValueTable = EventTriggerInputDeviceSetupValueTable
        self.__context = context

    def FindByCondition(self, condition: BinaryExpression):
        ins = self.__eventTriggerInputDeviceSetupValueTable.select().where(condition)
        rel = self.__context.execute(ins)
        return rel

    def UpdateByCondition(self, condition: BinaryExpression, values: dict):
        ins = self.__eventTriggerInputDeviceSetupValueTable.update().where(condition).values(values)
        self.__context.execute(ins)

    def Insert(self, values: dict):
        ins = self.__eventTriggerInputDeviceSetupValueTable.insert()
        self.__context.execute(ins, values)

    def InsertMany(self, values: list):
        ins = self.__eventTriggerInputDeviceSetupValueTable.insert()
        self.__context.execute(ins, values)

    def RemoveByCondition(self, condition: BinaryExpression):
        ins = self.__eventTriggerInputDeviceSetupValueTable.delete().where(condition)
        self.__context.execute(ins)
