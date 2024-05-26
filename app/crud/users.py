import datetime
from decimal import Decimal
from sqlalchemy.dialects.postgresql import insert as psg_insert
from sqlalchemy import (
    insert, select, update, and_
)
from app.config.database import async_engine
from app.database.models import (
    user_table, user_profile, user_models, user_payments
)


async def create_user_in_db(
    user_tg_id: int,
    user_core_id: int,
    email: str,
    password: str,
    model_id: int,
    model_name: str,
):
    async with async_engine.connect() as connect:
        stmt = (
            insert(user_table).
            values(
                user_tg_id=user_tg_id,
                user_core_id=user_core_id,
                email=email,
                password=password
            )
        )
        await connect.execute(stmt)

        stmt = (
            insert(user_profile).
            values(user_tg_id=user_tg_id)
        )
        await connect.execute(stmt)

        stmt = (
            insert(user_models).
            values(
                model_id=model_id,
                user_tg_id=user_tg_id,
                model_name=model_name,
                current=True
            )
        )

        await connect.execute(stmt)

        await connect.commit()

    await async_engine.dispose()


async def get_user_from_db(user_tg_id: int):
    async with async_engine.connect() as connect:

        stmt = (
            select(user_table.c["email", "password"]).
            where(user_table.c.user_tg_id == user_tg_id)
        )
        result = await connect.execute(stmt)

    await async_engine.dispose()

    return result.first()


async def get_user_dialogue_from_db(user_tg_id: int):
    async with async_engine.connect() as connect:

        stmt = (
            select(user_models.c["model_id", "dialogue_id", "number_dialogue"]).
            where(
                and_(
                    user_models.c.user_tg_id == user_tg_id,
                    user_models.c.current == True
                )
            )
        )
        result = await connect.execute(stmt)

    await async_engine.dispose()

    return result.first()


async def update_user_model_in_db(
    user_tg_id: int,
    model_id: int,
    model_name: str,
):
    async with async_engine.connect() as connect:

        update_cte = (
            update(user_models).
            values(current=False).
            where(
                and_(
                    user_models.c.user_tg_id == user_tg_id,
                    user_models.c.current == True
                )
            ).cte("cte")
        )

        insert_stmt = (
            psg_insert(user_models).
            values(
                model_id=model_id,
                user_tg_id=user_tg_id,
                model_name=model_name,
                current=True,
            ).
            add_cte(update_cte)
        )

        do_update_stmt = (
            insert_stmt.on_conflict_do_update(
                constraint=user_models.primary_key,
                set_=dict(current=True)
            )
        )

        await connect.execute(do_update_stmt)

        await connect.commit()

    await async_engine.dispose()


async def update_dialogue_user(user_tg_id: int, dialogue_id: int):
    async with async_engine.connect() as connect:

        stmt = (
            update(user_models).
            values(dialogue_id=dialogue_id).
            where(
                and_(
                    user_models.c.user_tg_id == user_tg_id,
                    user_models.c.current == True
                )
            )
        )

        await connect.execute(stmt)

        await connect.commit()

    await async_engine.dispose()


async def inc_number_dialogue_user(user_tg_id: int):
    async with async_engine.connect() as connect:

        stmt = (
            update(user_models).
            values(number_dialogue=user_models.c.number_dialogue + 1).
            where(
                and_(
                    user_models.c.user_tg_id == user_tg_id,
                    user_models.c.current == True
                )
            ).
            returning(
                user_models.c.model_id,
                user_models.c.number_dialogue,
            )
        )

        result = await connect.execute(stmt)

        await connect.commit()

    await async_engine.dispose()

    return result.first()


async def get_user_balance_from_db(user_tg_id: int):
    async with async_engine.connect() as connect:
        stmt = (
            select(user_profile.c.balance).
            where(
                user_profile.c.user_tg_id == user_tg_id
            )
        )
        result = await connect.execute(stmt)

    await async_engine.dispose()

    return result.scalar_one()


async def create_user_payment_in_db(
    user_tg_id: int,
    payment_id: str,
    recipient_id: str,
    status: str,
    amount: "Decimal",
    currency: str,
    created_at: "datetime",
):
    async with async_engine.connect() as connect:
        stmt = (
           insert(user_payments).
           values(
               user_tg_id=user_tg_id,
               payment_id=payment_id,
               recipient_id=recipient_id,
               status=status,
               amount=amount,
               currency=currency,
               created_at=created_at
           )
        )

        await connect.execute(stmt)
        await connect.commit()

    await async_engine.dispose()


async def increment_user_balance_in_db(
    user_tg_id: int,
    payment_id: str,
    status: str,
    amount: "Decimal",
    income_amount: "Decimal",
    captured_at: "datetime",
    receipt_registration: str
):
    async with async_engine.connect() as connect:
        update_cte = (
            update(user_payments).
            values(
                status=status,
                captured_at=captured_at,
                income_amount=income_amount,
                receipt_registration=receipt_registration
            ).
            where(user_payments.c.payment_id == payment_id)
        ).cte("cte")

        stmt = (
            update(user_profile).
            values(
                balance=(user_profile.c.balance + amount),
                update_at=datetime.datetime.now()
            ).
            where(user_profile.c.user_tg_id == int(user_tg_id))
        ).add_cte(update_cte)

        await connect.execute(stmt)
        await connect.commit()

    await async_engine.dispose()


async def cansel_payment_user_in_db(
    payment_id: str,
    status: str,
    cancellation_details: str
):
    async with async_engine.connect() as connect:

        stmt = (
            update(user_payments).
            values(
                status=status,
                cancellation_details=cancellation_details
            ).
            where(user_payments.c.payment_id == payment_id)
        )

        await connect.execute(stmt)
        await connect.commit()

    await async_engine.dispose()


async def decrement_user_balance_in_db(user_tg_id: int, amount: "Decimal"):
    async with async_engine.connect() as connect:
        stmt = (
            update(user_profile).
            values(balance=(user_profile.c.balance - amount)).
            where(user_profile.c.user_tg_id == user_tg_id)
        )

        await connect.execute(stmt)
        await connect.commit()

    await async_engine.dispose()