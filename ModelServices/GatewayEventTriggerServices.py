from Repository.EventTriggerRepo import EventTriggerRepo
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql.expression import BinaryExpression

from Repository.GatewayEventTriggerRepo import GatewayEventTriggerRepo


class MetaGatewayEventTriggerServices(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaGatewayEventTriggerServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GatewayEventTriggerServices(metaclass=MetaGatewayEventTriggerServices):
    __gatewayEventTriggerRepo: GatewayEventTriggerRepo

    def __init__(self, GatewayEventTriggerTable: Table, context: Connection):
        self.__gatewayEventTriggerRepo = GatewayEventTriggerRepo(GatewayEventTriggerTable, context)

    def FindGatewayEventTriggerById(self, Id: int):
        rel = self.__gatewayEventTriggerRepo.FindById(Id)
        return rel

    def UpdateGatewayEventTriggerCondition(self, condition: BinaryExpression, values: dict):
        self.__gatewayEventTriggerRepo.UpdateByCondition(condition, values)

    def InsertGatewayEventTrigger(self, values: dict):
        self.__gatewayEventTriggerRepo.Insert(values)

    def RemoveGatewayEventTriggerByCondition(self, condition: BinaryExpression):
        self.__gatewayEventTriggerRepo.RemoveByCondition(condition)