from sqlalchemy import Table
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.engine.base import Connection


class GatewayEventTriggerOutputRelayRepo:
    __gatewayEventTriggerOutputRelayTable: Table
    __context: Connection

    def __init__(self, GatewayEventTriggerOutputRelayTable: Table, context: Connection):
        self.__gatewayEventTriggerOutputRelayTable = GatewayEventTriggerOutputRelayTable
        self.__context = context

    def FindGatewayEventTriggerByCondition(self, condition: BinaryExpression):
        ins = self.__gatewayEventTriggerOutputRelayTable.select().where(condition)
        rel = self.__context.execute(ins)
        return rel

    def UpdateGatewayEventTriggerByCondition(self, condition: BinaryExpression, values: dict):
        ins = self.__gatewayEventTriggerOutputRelayTable.update().where(condition).values(values)
        self.__context.execute(ins)

    def InsertGatewayEventTrigger(self, values: dict):
        ins = self.__gatewayEventTriggerOutputRelayTable.insert()
        self.__context.execute(ins, values)

    def InsertManyGatewayEventTrigger(self, values: list):
        ins = self.__gatewayEventTriggerOutputRelayTable.insert()
        self.__context.execute(ins, values)

    def RemoveGatewayEventTriggerByCondition(self, condition: BinaryExpression):
        ins = self.__gatewayEventTriggerOutputRelayTable.delete().where(condition)
        print(ins)
        try:
            self.__context.execute(ins)
        except Exception as err:
            print(err)
