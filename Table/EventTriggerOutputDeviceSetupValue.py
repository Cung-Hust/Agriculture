from sqlalchemy import Float, Integer
from sqlalchemy import Table, Column, String, MetaData


class EventTriggerOutputDeviceSetupValue:
    def __init__(self, metadata: MetaData):
        self.eventTriggerOutputDeviceSetupValue = Table('EventTriggerOutputDeviceSetupValue', metadata,
                                                        Column('EventTriggerId', Integer, primary_key=True,
                                                               nullable=False),
                                                        Column('DeviceAddress', String, primary_key=True,
                                                               nullable=False),
                                                        Column('PropertyId', Integer, primary_key=True, nullable=False),
                                                        Column('PropertyValue', Float),
                                                        )
