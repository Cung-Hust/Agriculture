from sqlalchemy import Table
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.engine.base import Connection


class NetworkRepo:
    __networkTable: Table
    __context: Connection

    def __init__(self, NetworkTable: Table, context: Connection):
        self.__networkTable = NetworkTable
        self.__context = context

    def FindById(self, Id: int):
        ins = self.__networkTable.select().where(self.__networkTable.c.NetworkId == Id)
        rel = self.__context.execute(ins)
        return rel

    def UpdateByCondition(self, condition: BinaryExpression, values: dict):
        ins = self.__networkTable.update().where(condition).values(values)
        self.__context.execute(ins)

    def Insert(self, values: dict):
        ins = self.__networkTable.insert()
        self.__context.execute(ins, values)

