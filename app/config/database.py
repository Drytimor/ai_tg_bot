from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine
from .config import settings


async_engine = create_async_engine(
    url=settings.sqlalchemy_database_uri
)

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(
    naming_convention=naming_convention,
)