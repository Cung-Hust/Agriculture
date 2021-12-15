from sqlalchemy import Float, Integer
from sqlalchemy import Table, Column, String, MetaData


class GatewayEventTriggerInputDeviceSetupValue:
    def __init__(self, metadata: MetaData):
        self.gatewayEventTriggerInputDeviceSetupValue = Table('GatewayEventTriggerInputDeviceSetupValue', metadata,
                                                       Column('EventTriggerId', Integer, primary_key=True,
                                                              nullable=False),
                                                       Column('DeviceAddress', String, primary_key=True,
                                                              nullable=False),
                                                       Column('PropertyId', Integer),
                                                       Column('PropertyValue', Float),
                                                       Column('Operation', Integer)
                                                       )
