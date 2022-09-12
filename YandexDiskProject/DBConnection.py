import databases
from sqlalchemy import (
    Column, Enum as PgEnum, ForeignKey, Integer,
    String, Table, MetaData, create_engine
)
from enum import Enum, unique


@unique
class FileType(Enum):
    file = 'FILE'
    folder = 'FOLDER'


class DataBaseConnection:
    DATABASE_URL = "postgresql://postgres:nastya1234@localhost:5433/yandex_test"

    database = databases.Database(DATABASE_URL)

    metadata = MetaData()

    def __init__(self):
        self.items_table = Table(
            "items",
            self.metadata,
            Column("id", String, primary_key=True),
            Column("url", String(255), nullable=True),
            Column("date", String, nullable=False),
            Column("parentId", String, nullable=True),
            Column("type", PgEnum(FileType), nullable=False),
            Column("size", Integer, nullable=True),
        )

        self.connections_table = Table(
            'connections',
            self.metadata,
            Column('itemId', String, ForeignKey('items.id'), primary_key=True),
            Column('parentId', String, nullable=True),
        )

        engine = create_engine(self.DATABASE_URL)
        self.metadata.create_all(engine)
