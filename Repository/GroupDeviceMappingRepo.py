from sqlalchemy import Table
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.engine.base import Connection


class GroupDeviceMappingRepo:
    __groupDeviceMappingTable: Table
    __context: Connection

    def __init__(self, GroupDeviceMappingTable: Table, context: Connection):
        self.__groupDeviceMappingTable = GroupDeviceMappingTable
        self.__context = context

    def Insert(self, values: dict):
        ins = self.__groupDeviceMappingTable.insert()
        self.__context.execute(ins, values)

    def InsertMany(self, values: list):
        ins = self.__groupDeviceMappingTable.insert()
        self.__context.execute(ins, values)

    def RemoveByCondition(self, condition: BinaryExpression):
        ins = self.__groupDeviceMappingTable.delete().where(condition)
        try:
            self.__context.execute(ins)
        except:
            pass

    def FindByCondition(self, condition: BinaryExpression):
        ins = self.__groupDeviceMappingTable.select().where(condition)
        rel = self.__context.execute(ins)
        return rel