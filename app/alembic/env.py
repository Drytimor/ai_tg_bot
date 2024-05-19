from logging.config import fileConfig
import asyncio
import sys
from pathlib import Path
import os
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here

sys.path.append(os.path.join(sys.path[0], Path().resolve().parent))
from app.database.models import metadata
from app.config.config import settings

target_metadata = metadata
section = config.config_ini_section
config.set_section_option(section, 'sqlalchemy_database_uri', settings.sqlalchemy_database_uri)


# # other values from the config, defined by the needs of env.py,
# # can be acquired:
# # my_important_option = config.get_main_option("my_important_option")
# # ... etc.
#
#

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online():
    """Run migrations in 'online' mode.
    """
    connectable = config.attributes.get("connection", None)

asyncio.run(run_async_migrations())
