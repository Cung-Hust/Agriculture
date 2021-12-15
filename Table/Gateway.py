from sqlalchemy import Integer, Boolean, Float
from sqlalchemy import Table, Column, String, MetaData


class Gateway:
    def __init__(self, metadata: MetaData):
        self.gateway = Table('Gateway', metadata,
                             Column('GatewayId', Integer,
                                    primary_key=True, nullable=False),
                             Column('Temp', Float),
                             Column('Lux', Float),
                             Column('U', Float),
                             Column('I', Float),
                             Column('Cos', Float),
                             Column('P', Float),
                             Column('Minute', Integer),
                             Column('KWH', Float),
                             Column('Scene', Integer),
                             Column('Ip', String),
                             Column('ActiveTime', Integer),
                             Column('Scene_1', Integer),
                             Column('Scene_2', Integer),
                             Column('Scene_3', Integer),
                             Column('Scene_4', Integer),
                             Column('Minute_1', Integer),
                             Column('Minute_2', Integer),
                             Column('Minute_3', Integer),
                             Column('Minute_4', Integer),
                             Column('Status', Integer),
                             Column('Relay_1', Boolean),
                             Column('Relay_2', Boolean),
                             Column('Relay_3', Boolean),
                             Column('Relay_4', Boolean)

                             )
