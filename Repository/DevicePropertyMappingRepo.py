from sqlalchemy import Table, bindparam, and_, case
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.engine.base import Connection


class DevicePropertyMappingRepo:
    __devicePropertyMappingTable: Table
    __context: Connection

    def __init__(self, devicePropertyMappingTable: Table, context: Connection):
        self.__devicePropertyMappingTable = devicePropertyMappingTable
        self.__context = context

    def UpdateByCondition(self, condition: BinaryExpression, values: dict):
        ins = self.__devicePropertyMappingTable.update().where(condition).values(values)
        self.__context.execute(ins)

    def FindByCondition(self, condition: BinaryExpression):
        ins = self.__devicePropertyMappingTable.select().where(condition)
        rel = self.__context.execute(ins)
        return rel

    def FindAll(self):
        ins = self.__devicePropertyMappingTable.select()
        rel = self.__context.execute(ins)
        return rel

    def RemoveByCondition(self, condition: BinaryExpression):
        ins = self.__devicePropertyMappingTable.delete().where(condition)
        self.__context.execute(ins)

    def UpdateManyByCustomConditionType1(self, data: list):
        print(data)
        ins = self.__devicePropertyMappingTable.update().where(
            and_(
                self.__devicePropertyMappingTable.c.DeviceAddress == bindparam("b_DeviceAddress"),
                self.__devicePropertyMappingTable.c.PropertyId == bindparam("b_PropertyId")
            )
        ).values({
            "PropertyValue": bindparam("b_PropertyValue")
        })
        self.__context.execute(ins, data)

    def InsertMany(self, values: list):
        ins = self.__devicePropertyMappingTable.insert()
        self.__context.execute(ins, values)