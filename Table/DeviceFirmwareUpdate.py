from sqlalchemy import Table, Column, String, MetaData


class DeviceFirmwareUpdate:
    def __init__(self, metadata: MetaData):
        self.deviceFirmwareUpdate = Table('DeviceFirmwareUpdate', metadata,
                                          Column('Id', String, primary_key=True, nullable=False),
                                          Column('Version', String),
                                          Column('Url', String),
                                          )
