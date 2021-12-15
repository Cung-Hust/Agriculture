from sqlalchemy import Table
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.engine.base import Connection


class GatewayRepo:
    __gatewayTable: Table
    __context: Connection

    def __init__(self, GatewayTable: Table, context: Connection):
        self.__gatewayTable = GatewayTable
        self.__context = context

    def FindById(self, Id: int):
        ins = self.__gatewayTable.select().where(self.__gatewayTable.c.GatewayId == Id)
        rel = self.__context.execute(ins)
        return rel

    def UpdateById(self, Id: int, values: dict):
        ins = self.__gatewayTable.update().where(self.__gatewayTable.c.GatewayId == Id).values(values)
        self.__context.execute(ins)

    def Insert(self, values: dict):
        ins = self.__gatewayTable.insert()
        self.__context.execute(ins, values)

