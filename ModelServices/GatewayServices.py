from Repository.GatewayRepo import GatewayRepo
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql.expression import BinaryExpression


class MetaGatewayServices(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaGatewayServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GatewayServices(metaclass=MetaGatewayServices):
    __gatewayRepo: GatewayRepo

    def __init__(self, GatewayTable: Table, context: Connection):
        self.__gatewayRepo = GatewayRepo(GatewayTable, context)

    def FindGatewayById(self, Id: int):
        rel = self.__gatewayRepo.FindById(Id)
        return rel

    def UpdateGatewayById(self, Id: int, values: dict):
        self.__gatewayRepo.UpdateById(Id, values)

    def InsertGateway(self, values: dict):
        self.__gatewayRepo.Insert(values)