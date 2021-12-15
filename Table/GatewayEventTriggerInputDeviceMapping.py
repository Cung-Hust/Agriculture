from sqlalchemy import Float, Integer
from sqlalchemy import Table, Column, String, MetaData


class GatewayEventTriggerInputDeviceMapping:
    def __init__(self, metadata: MetaData):
        self.gatewayEventTriggerInputDeviceMapping = Table('GatewayEventTriggerInputDeviceMapping', metadata,
                                                           Column('EventTriggerId', Integer, primary_key=True,
                                                                  nullable=False),
                                                           Column('DeviceAddress', String, primary_key=True,
                                                                  nullable=False),
                                                           )
