from sqlalchemy import Integer, Float
from sqlalchemy import Table, Column, String, MetaData


class DevicePropertyMapping:
    def __init__(self, metadata: MetaData):
        self.devicePropertyMapping = Table('DevicePropertyMapping', metadata,
                                           Column('DeviceAddress', String, primary_key=True, nullable=False),
                                           Column('PropertyId', Integer, primary_key=True, nullable=False),
                                           Column('PropertyValue', Float),
                                           )
