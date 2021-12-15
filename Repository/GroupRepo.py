from sqlalchemy import Table
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.engine.base import Connection


class GroupRepo:
    __groupTable: Table
    __context: Connection

    def __init__(self, GroupTable: Table, context: Connection):
        self.__groupTable = GroupTable
        self.__context = context

    def UpdateByCondition(self, condition: BinaryExpression, values: dict):
        ins = self.__groupTable.update().where(condition).values(values)
        self.__context.execute(ins)

    def FindByCondition(self, condition: BinaryExpression):
        ins = self.__groupTable.select().where(condition)
        rel = self.__context.execute(ins)
        return rel

    def FindAll(self):
        ins = self.__groupTable.select()
        rel = self.__context.execute(ins)
        return rel

    def Insert(self, values: dict):
        ins = self.__groupTable.insert()
        self.__context.execute(ins, values)
