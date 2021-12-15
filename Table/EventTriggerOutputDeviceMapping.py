from sqlalchemy import Boolean, Integer
from sqlalchemy import Table, Column, String, MetaData


class EventTriggerOutputDeviceMapping:
    def __init__(self, metadata: MetaData):
        self.eventTriggerOutputDeviceMapping = Table('EventTriggerOutputDeviceMapping', metadata,
                                                     Column('EventTriggerId', Integer, primary_key=True,
                                                            nullable=False),
                                                     Column(
                                                         'DeviceAddress', String, primary_key=True, nullable=False),
                                                     Column(
                                                         'IsEnable', Boolean),
                                                     Column('Success', Boolean)
                                                     )
