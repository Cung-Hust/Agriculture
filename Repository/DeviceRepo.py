from sqlalchemy import Table
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.engine.base import Connection


class DeviceRepo:
    __deviceTable: Table
    __context: Connection

    def __init__(self, DeviceTable: Table, context: Connection):
        self.__deviceTable = DeviceTable
        self.__context = context

    def UpdateByCondition(self, condition: BinaryExpression, values: dict):
        ins = self.__deviceTable.update().where(condition).values(values)
        self.__context.execute(ins)

    def FindByCondition(self, condition: BinaryExpression):
        ins = self.__deviceTable.select().where(condition)
        rel = self.__context.execute(ins)
        return rel

    def FindAll(self):
        ins = self.__deviceTable.select()
        rel = self.__context.execute(ins)
        return rel

    def RemoveByCondition(self, condition: BinaryExpression):
        ins = self.__deviceTable.delete().where(condition)
        self.__context.execute(ins)

    def FindAllDeviceAddress(self):
        ins = self.__deviceTable.select(self.__deviceTable.c.DeviceAddress)
        rel = self.__context.execute(ins)
        return rel

    def InsertMany(self, values: list):
        ins = self.__deviceTable.insert()
        self.__context.execute(ins, values)
