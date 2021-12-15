import asyncio
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.engine.base import Connection
import Constants.Constant as Const
from Table.TableManager import TableManager
from ModelServices.ServicesManager import ServicesManager
from sqlalchemy.pool import StaticPool


class MetaDb(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaDb, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Db(metaclass=MetaDb):
    __metadata = MetaData()
    __engine: create_engine
    __connect: Connection
    __tables: TableManager
    __services: ServicesManager

    def init(self):
        self.__engine = create_engine('sqlite:///' + Const.DB_NAME, echo=True,
                                      connect_args={'check_same_thread': False}, poolclass=StaticPool)
        self.__tables = TableManager(self.__metadata)
        self.__metadata.create_all(self.__engine)
        self.__connect = self.__engine.connect()
        self.__services = ServicesManager(self.__tables, self.__connect)

    @property
    def Table(self):
        return self.__tables

    @property
    def Services(self):
        return self.__services
