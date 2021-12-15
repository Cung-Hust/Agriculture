from sqlalchemy import Float, Integer
from sqlalchemy import Table, Column, String, MetaData


class EventTriggerOutputGroupSetupValue:
    def __init__(self, metadata: MetaData):
        self.eventTriggerOutputGroupSetupValue = Table('EventTriggerOutputGroupSetupValue', metadata,
                                                       Column('EventTriggerId', Integer, primary_key=True,
                                                              nullable=False),
                                                       Column('GroupId', String, primary_key=True, nullable=False),
                                                       Column('PropertyId', Integer, primary_key=True, nullable=False),
                                                       Column('PropertyValue', Float),
                                                       )
