from sqlalchemy import Float, Integer, Boolean
from sqlalchemy import Table, Column, String, MetaData


class GroupDeviceMapping:
    def __init__(self, metadata: MetaData):
        self.groupDeviceMapping = Table('GroupDeviceMapping', metadata,
                                        Column('GroupId', Integer,
                                               primary_key=True, nullable=False),
                                        Column('DeviceAddress', String,
                                               primary_key=True, nullable=False),
                                        Column('Number', Integer),
                                        Column('Success', Boolean)
                                        )
