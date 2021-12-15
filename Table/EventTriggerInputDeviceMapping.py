from sqlalchemy import Float, Integer
from sqlalchemy import Table, Column, String, MetaData


class EventTriggerInputDeviceMapping:
    def __init__(self, metadata: MetaData):
        self.eventTriggerInputDeviceMapping = Table('EventTriggerInputDeviceMapping', metadata,
                                                    Column('EventTriggerId', Integer, primary_key=True, nullable=False),
                                                    Column('DeviceAddress', String, primary_key=True, nullable=False),
                                                    )
