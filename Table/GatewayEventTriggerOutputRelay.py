from sqlalchemy import Float, Integer, Boolean
from sqlalchemy import Table, Column, String, MetaData


class GatewayEventTriggerOutputRelay:
    def __init__(self, metadata: MetaData):
        self.gatewayEventTriggerOutputRelay = Table('GatewayEventTriggerOutputRelay', metadata,
                                                        Column('EventTriggerId', Integer, primary_key=True,
                                                               nullable=False),
                                                        Column('Relay', String, primary_key=True,
                                                               nullable=False),
                                                        Column('Value', Boolean),
                                                        )
