from Repository.GroupDeviceMappingRepo import GroupDeviceMappingRepo
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql.expression import BinaryExpression


class MetaGroupDeviceMappingServices(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaGroupDeviceMappingServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GroupDeviceMappingServices(metaclass=MetaGroupDeviceMappingServices):
    __groupDeviceMappingRepo: GroupDeviceMappingRepo

    def __init__(self, GroupDeviceMappingTable: Table, context: Connection):
        self.__groupDeviceMappingRepo = GroupDeviceMappingRepo(GroupDeviceMappingTable, context)

    def InsertManyGroupDeviceMapping(self, values: list):
        self.__groupDeviceMappingRepo.InsertMany(values)

    def RemoveGroupDeviceMappingByCondition(self, condition: BinaryExpression):
        self.__groupDeviceMappingRepo.RemoveByCondition(condition)

    def FindGroupDeviceMappingByCondition(self, condition: BinaryExpression):
        rel = self.__groupDeviceMappingRepo.FindByCondition(condition)
        return rel