from sqlalchemy import Boolean, Integer
from sqlalchemy import Table, Column, String, MetaData


class EventTriggerOutputGroupMapping:
    def __init__(self, metadata: MetaData):
        self.eventTriggerOutputGroupMapping = Table('EventTriggerOutputGroupMapping', metadata,
                                                    Column('EventTriggerId', Integer, primary_key=True, nullable=False),
                                                    Column('GroupId', String, primary_key=True, nullable=False),
                                                    Column('IsEnable', Boolean)
                                                    )
