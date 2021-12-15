from Repository.NetworkRepo import NetworkRepo
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql.expression import BinaryExpression


class MetaNetworkServices(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaNetworkServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class NetworkServices(metaclass=MetaNetworkServices):
    __networkRepo: NetworkRepo

    def __init__(self, NetworkTable: Table, context: Connection):
        self.__networkRepo = NetworkRepo(NetworkTable, context)

    def FindNetworkById(self, Id: int):
        rel = self.__networkRepo.FindById(Id)
        return rel

    def UpdateNetworkByCondition(self, condition: BinaryExpression, values: dict):
        self.__networkRepo.UpdateByCondition(condition, values)

    def InsertNetwork(self, values: dict):
        self.__networkRepo.Insert(values)