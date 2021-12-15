from sqlalchemy import Boolean, Integer
from sqlalchemy import Table, Column, String, MetaData


class EventTrigger:
    def __init__(self, metadata: MetaData):
        self.eventTrigger = Table('EventTrigger', metadata,
                                  Column('EventTriggerId', Integer, primary_key=True, nullable=False),
                                  Column('Name', String),
                                  Column('ScheduleRaw', String),
                                  Column('ScheduleId', Integer),
                                  Column('ScriptType', Integer),
                                  Column('IsEnable', Boolean),
                                  )
