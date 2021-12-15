from Repository.GatewayEventTriggerOutputRelayRepo import GatewayEventTriggerOutputRelayRepo
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql.expression import BinaryExpression


class MetaGatewayEventTriggerOutputRelayServices(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaGatewayEventTriggerOutputRelayServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GatewayEventTriggerOutputRelayServices(metaclass=MetaGatewayEventTriggerOutputRelayServices):
    __gatewayEventTriggerOutputRelayRepo: GatewayEventTriggerOutputRelayRepo

    def __init__(self, EventTriggerOutputDeviceSetupValueTable: Table, context: Connection):
        self.__gatewayEventTriggerOutputRelayRepo = GatewayEventTriggerOutputRelayRepo(EventTriggerOutputDeviceSetupValueTable, context)

    def FindEventTriggerOutputDeviceSetupValueByCondition(self, condition: BinaryExpression):
        rel = self.__gatewayEventTriggerOutputRelayRepo.FindGatewayEventTriggerByCondition(condition)
        return rel

    def UpdateEventTriggerOutputRelayByCondition(self, condition: BinaryExpression, values: dict):
        self.__gatewayEventTriggerOutputRelayRepo.UpdateGatewayEventTriggerByCondition(condition, values)

    def InsertEventTriggerOutputRelay(self, values: dict):
        self.__gatewayEventTriggerOutputRelayRepo.InsertGatewayEventTrigger(values)

    def InsertManyEventTriggerOutputRelay(self, values: list):
        self.__gatewayEventTriggerOutputRelayRepo.InsertManyGatewayEventTrigger(values)

    def RemoveEventTriggerOutputRelayByCondition(self, condition: BinaryExpression):
        self.__gatewayEventTriggerOutputRelayRepo.RemoveGatewayEventTriggerByCondition(condition)
        print("Delete - 3")