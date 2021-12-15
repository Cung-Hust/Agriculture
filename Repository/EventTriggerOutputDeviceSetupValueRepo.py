from sqlalchemy import Table
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.engine.base import Connection


class EventTriggerOutputDeviceSetupValueRepo:
    __eventTriggerOutputDeviceSetupValueTable: Table
    __context: Connection

    def __init__(self, EventTriggerOutputDeviceSetupValueTable: Table, context: Connection):
        self.__eventTriggerOutputDeviceSetupValueTable = EventTriggerOutputDeviceSetupValueTable
        self.__context = context

    def FindByCondition(self, condition: BinaryExpression):
        ins = self.__eventTriggerOutputDeviceSetupValueTable.select().where(condition)
        rel = self.__context.execute(ins)
        return rel

    def UpdateByCondition(self, condition: BinaryExpression, values: dict):
        ins = self.__eventTriggerOutputDeviceSetupValueTable.update().where(condition).values(values)
        self.__context.execute(ins)

    def Insert(self, values: dict):
        ins = self.__eventTriggerOutputDeviceSetupValueTable.insert()
        self.__context.execute(ins, values)

    def InsertMany(self, values: list):
        ins = self.__eventTriggerOutputDeviceSetupValueTable.insert()
        self.__context.execute(ins, values)

    def RemoveByCondition(self, condition: BinaryExpression):
        ins = self.__eventTriggerOutputDeviceSetupValueTable.delete().where(condition)
        print(ins)
        try:
            self.__context.execute(ins)
        except Exception as err:
            print(err)
