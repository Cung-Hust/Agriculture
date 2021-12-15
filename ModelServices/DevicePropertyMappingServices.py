from Repository.DevicePropertyMappingRepo import DevicePropertyMappingRepo
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql.expression import BinaryExpression


class MetaDevicePropertyMappingServices(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaDevicePropertyMappingServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DevicePropertyMappingServices(metaclass=MetaDevicePropertyMappingServices):
    __devicePropertyMappingRepo: DevicePropertyMappingRepo

    def __init__(self, DevicePropertyTable: Table, context: Connection):
        self.__devicePropertyMappingRepo = DevicePropertyMappingRepo(DevicePropertyTable, context)

    def UpdateManyDevicePropertyMappingCustomByConditionType1(self, data: list):
        self.__devicePropertyMappingRepo.UpdateManyByCustomConditionType1(data)

    def FindDevicePropertyMappingByCondition(self, condition: BinaryExpression):
        rel = self.__devicePropertyMappingRepo.FindByCondition(condition)
        return rel

    def RemoveDevicePropertyMappingByCondition(self, condition: BinaryExpression):
        self.__devicePropertyMappingRepo.RemoveByCondition(condition)

    def FindAllDevicePropertyMapping(self):
        rel = self.__devicePropertyMappingRepo.FindAll()
        return rel

    def InsertManyDevicePropertyMapping(self, values: list):
        self.__devicePropertyMappingRepo.InsertMany(values)