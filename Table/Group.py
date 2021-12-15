from sqlalchemy import Integer
from sqlalchemy import Table, Column, String, MetaData


class Group:
    def __init__(self, metadata: MetaData):
        self.group = Table('Group', metadata,
                           Column('GroupId', Integer, primary_key=True, nullable=False),
                           Column('Name', String),
                           )
