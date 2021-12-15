from sqlalchemy import Integer
from sqlalchemy import Table, Column, String, MetaData


class Property:
    def __init__(self, metadata: MetaData):
        self.property = Table('Property', metadata,
                              Column('PropertyId', Integer, primary_key=True, nullable=False),
                              Column('Name', String, unique=True),
                              )
