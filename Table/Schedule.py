from sqlalchemy import Float, Integer, Boolean
from sqlalchemy import Table, Column, String, MetaData


class Schedule:
    def __init__(self, metadata: MetaData):
        self.schedule = Table('Schedule', metadata,
                              Column('ScheduleId', Integer, primary_key=True, nullable=False),
                              Column('IsRepeat', Boolean),
                              Column('Secs', Integer),
                              Column('Minutes', Integer),
                              Column('Hours', Integer),
                              Column('Days', Integer),
                              Column('Monday', Boolean),
                              Column('Tuesday', Boolean),
                              Column('Wednesday', Boolean),
                              Column('Thursday', Boolean),
                              Column('Friday', Boolean),
                              Column('Saturday', Boolean),
                              Column('Sunday', Boolean),
                              Column('AtTime', Integer),
                              Column('FromTime', Integer),
                              Column('ToTime', Integer),
                              )
