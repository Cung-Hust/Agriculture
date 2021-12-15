from Repository.GroupRepo import GroupRepo
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql.expression import BinaryExpression


class MetaGroupServices(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaGroupServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GroupServices(metaclass=MetaGroupServices):
    __groupRepo: GroupRepo

    def __init__(self, GroupTable: Table, context: Connection):
        self.__groupRepo = GroupRepo(GroupTable, context)

    def InsertGroup(self, values: dict):
        self.__groupRepo.Insert(values)

    def FindGroupByCondition(self, condition: BinaryExpression):
        rel = self.__groupRepo.FindByCondition(condition)
        return rel

    def FindAllGroup(self):
        rel = self.__groupRepo.FindAll()
        return rel
