from Repository.DeviceRepo import DeviceRepo
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql.expression import BinaryExpression


class MetaDeviceServices(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaDeviceServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DeviceServices(metaclass=MetaDeviceServices):
    __deviceRepo: DeviceRepo

    def __init__(self, DeviceTable: Table, context: Connection):
        self.__deviceRepo = DeviceRepo(DeviceTable, context)

    def UpdateDeviceByCondition(self, condition: BinaryExpression, values: dict):
        self.__deviceRepo.UpdateByCondition(condition, values)

    def FindDeviceByCondition(self, condition: BinaryExpression):
        rel = self.__deviceRepo.FindByCondition(condition)
        return rel

    def FindAllDevice(self):
        rel = self.__deviceRepo.FindAll()
        return rel

    def RemoveDeviceByCondition(self, condition: BinaryExpression):
        self.__deviceRepo.RemoveByCondition(condition)

    def FindAllDeviceAddress(self):
        rel = self.__deviceRepo.FindAllDeviceAddress()
        return rel

    def InsertMany(self, values: list):
        rel = self.__deviceRepo.InsertMany(values)