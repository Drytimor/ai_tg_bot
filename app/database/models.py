from datetime import datetime
from sqlalchemy import (
    Table, Column, String, DateTime, BigInteger, Numeric,
    func, Integer, Boolean, ForeignKeyConstraint, PrimaryKeyConstraint, text
)
from app.config.database import metadata


user_table = Table(
    "users",
    metadata,
    Column("user_tg_id", primary_key=True, autoincrement=False),
    Column("user_core_id", BigInteger, nullable=False, unique=True),
    Column("email", String(255), nullable=False, unique=True),
    Column("password", String(255), nullable=False),
    Column('created_at', DateTime, server_default=func.current_timestamp(), nullable=False),
)

user_profile = Table(
    "user_profile",
    metadata,
    Column("user_tg_id", primary_key=True, autoincrement=False),
    Column("balance", Numeric(10, 2), default=0, nullable=False),
    Column(
        "update_at",
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=datetime.now(),
        nullable=False
    ),
    ForeignKeyConstraint(
        ["user_tg_id"],
        ["users.user_tg_id"],
        onupdate="CASCADE", ondelete="CASCADE"
    )
)


user_models = Table(
    "user_models",
    metadata,
    Column("model_id", Integer, nullable=False),
    Column("user_tg_id", BigInteger, nullable=False),
    Column("model_name", String(255), nullable=False),
    Column("dialogue_id", BigInteger, server_default=text("0")),
    Column("number_dialogue", BigInteger, server_default=text("0")),
    Column("current", Boolean, default=False, nullable=False),
    PrimaryKeyConstraint(
        "model_id", "user_tg_id",
        name="pk_user_models_user_tg_id_model_id"
    ),
    ForeignKeyConstraint(
        ["user_tg_id"],
        ["user_profile.user_tg_id"],
        onupdate="CASCADE", ondelete="CASCADE"
    )
)
