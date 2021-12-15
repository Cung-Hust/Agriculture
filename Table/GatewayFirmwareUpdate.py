from sqlalchemy import Table, Column, String, MetaData


class GatewayFirmwareUpdate:
    def __init__(self, metadata: MetaData):
        self.gatewayFirmwareUpdate = Table('GatewayFirmwareUpdate', metadata,
                                           Column('Id', String, primary_key=True, nullable=False),
                                           Column('Version', String),
                                           Column('Url', String),
                                           )
