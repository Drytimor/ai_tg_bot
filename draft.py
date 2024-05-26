import asyncio
import datetime
import decimal
import time
from sqlalchemy import update, and_
from sqlalchemy.dialects.postgresql import insert

from app.config.config import settings
from app.config.database import async_engine
from app.database.models import (
    user_table,
    user_models
)
from app.core_api.route import (
    login_user_in_core,
    create_dialog,
    create_message,
    create_user_in_core, route_yookassa
)
from app.crud.users import (
    create_user_in_db,
    get_user_dialogue_from_db,
    inc_number_dialogue_user,
    update_user_model_in_db,
    increment_user_balance_in_db
)
from app.services.cache import (
    set_user_dialogue_in_cache,
    get_user_dialogue_from_cache,
    del_user_dialogue_from_cache
)
from app.services.payment import create_payment_in_yookassa

"""
with update_models as (
    update user_models set current = false where model_id != 1 and user_tg_id = 1351751029
)
insert into user_models (model_id, user_tg_id, model_name, dialogue_id, number_dialogue, current) 
values (1, 1351751029,'gpt-3.5-turbo', 0, 0, true)
on conflict on constraint pk_user_models_user_tg_id_model_id
do update set current = true;
"""

if __name__ == '__main__':
    func = increment_user_balance_in_db(
        user_tg_id=1351751029, payment_id="2de2bfaa-000f-5000-8000-1f7f9b0a0e91",
        status="succeeded", amount=decimal.Decimal(1),
        income_amount=decimal.Decimal(1), captured_at=datetime.datetime.now(),
        receipt_registration="succeeded"
    )
    res = asyncio.run(func)

    # func = inc_number_dialogue_user(user_id)
    # func = update_user_model_in_db(user_id, model_id, model_name)
    # func = get_user_dialogue_from_db(user_id)
    # func = del_user_dialogue_from_cache(user_id)
    # print(res.number_dialogue)
    # func = create_user_in_db(tg_id, core_id, email, password, 1, 'bot')
    # func = set_user_dialogue_in_cache(1, 1, 2)
    # func = get_user_dialogue_from_cache(1)
    # {"id":109,"name":"dialogue 0","bot_id":1}
    # func = create_user_in_db(tg_id, core_id, email, password)
    # response = await login("bob123@mail.ru", "123")
    # func = set_token_in_cache("bob123@mail.ru", "123", expires_in=1715522982)
    # func = create_user_in_core('tg-23123113@mail.com', "123")
    # func = login_user_in_core('tg-23123113@mail.com', "123")
    # func = create_dialog(token, "dialogue 0", 1)
    # {"id":110,"name":"dialogue 0","bot_id":1}
    # func = create_message(token, dialogue, 1, "hi")
    # func = get_user_from_db(1351751029)




# 1351751029
# user_core_id | 20
# email        | id-1351751029@telegram.org
# password     | 1351751029
# balance      | 0.00
# created_at   | 2024-05-11 22:42:13.904209


