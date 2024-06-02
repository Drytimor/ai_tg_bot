from datetime import datetime
from decimal import Decimal
from app.core_api.route import (
    create_payment_in_yookassa,
    get_current_info_user_payment
)
from app.crud.users import (
    create_user_payment_in_db,
    increment_user_balance_in_db,
    cansel_payment_user_in_db
)
from app.log.log import (
    PaymentError,
    msg_payment_error,
    msg_error_answer,
    logger_payment,
    logger_raw_exc,
)
from app.bot.text import (
    msg_confirmation_url,
    msg_success_up_balance,
    msg_fail_up_balance
)
from app.services.cache import set_context_limit_in_cache


async def create_payment_for_user(
    user_tg_id: int,
    user_chat_id: int,
    amount: str,
):

    await set_context_limit_in_cache(user_tg_id)

    message_answer = "%s"
    try:
        payment = await create_payment_in_yookassa(
            user_tg_id=user_tg_id,
            user_chat_id=user_chat_id,
            amount=amount,
        )
    except PaymentError:
        message_answer = message_answer % msg_payment_error

    except Exception as exc:
        logger_raw_exc.error(exc_info=True, msg=exc.args)
        message_answer = message_answer % msg_error_answer

    else:
        await create_user_payment_in_db(
            user_tg_id=user_tg_id,
            payment_id=payment["id"],
            recipient_id=payment["recipient"]["account_id"],
            status=payment["status"],
            amount=Decimal(payment["amount"]["value"]),
            currency=payment["amount"]["currency"],
            created_at=datetime.strptime(payment["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        )
        confirmation_url = payment["confirmation"]["confirmation_url"]
        message_answer = message_answer % (msg_confirmation_url % confirmation_url)

    return message_answer


async def update_user_payment_status(webhook_data: dict):

    webhook_object = webhook_data["object"]
    user_tg_id = webhook_object["metadata"]["user_tg_id"]
    payment_id = webhook_object["id"]

    current_payment = await get_current_info_user_payment(
        payment_id=payment_id, user_tg_id=user_tg_id
    )
    payment_status = current_payment["status"]
    user_chat_id = current_payment["metadata"]["user_chat_id"]

    if payment_status != webhook_object["status"]:
        logger_payment.error("error")
        raise PaymentError(msg_payment_error)

    massage_answer = "%s"
    data = {
        "payment_id": payment_id,
        "status": payment_status,
    }
    if payment_status == "succeeded":
        massage_answer = massage_answer % msg_success_up_balance

        data.update({
            "user_tg_id": user_tg_id,
            "amount": Decimal(current_payment["amount"]["value"]),
            "income_amount": Decimal(current_payment["income_amount"]["value"]),
            "captured_at": datetime.strptime(current_payment["captured_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        })
        await increment_user_balance_in_db(**data)

    elif payment_status == "canceled":
        massage_answer = massage_answer % msg_fail_up_balance
        # data["cancellation_details"] = current_payment["cancellation_details"]["reason"],
        data["cancellation_details"] = "fail"
        await cansel_payment_user_in_db(**data)

    else:
        logger_raw_exc.warning(webhook_object)
        raise PaymentError(msg_payment_error)

    return user_chat_id, massage_answer


"""
{'id': '2ddf8f3d-000f-5000-8000-1efd353a2846', 
'status': 'pending', 
'amount': {'value': '100.00', 'currency': 'RUB'}, 
'description': 'Заказ №10', 
'recipient': {'account_id': '303569', 'gateway_id': '2168064'}, 
'created_at': '2024-05-22T04:58:37.278Z', 
'confirmation': {'type': 'redirect', 
'confirmation_url':'https://yoomoney.ru/checkout/payments/v2/contract?orderId=2ddf8f3d-000f-5000-8000-1efd353a2846'}, 
'test': True, 
'paid': False, 
'refundable': False, 
'metadata': {'orderNumber': '10'}}


{'type': 'notification', 
'event': 'payment.succeeded', 
'object': {'id': '2ddf8f3d-000f-5000-8000-1efd353a2846', 
'status': 'succeeded', 
'amount': {'value': '100.00', 'currency': 'RUB'}, 
'income_amount': {'value': '96.50', 'currency': 'RUB'}, 
'description': 'Заказ №10', 
'recipient': {'account_id': '303569', 'gateway_id': '2168064'}, 
'payment_method': {'type': 'bank_card', 
'id': '2ddf8f3d-000f-5000-8000-1efd353a2846', 
'saved': False, 
'title': 'Bank card *0079', 
'card': {'first6': '220000', 'last4': '0079', 'expiry_year': '2028', 'expiry_month': '10', 'card_type': 'Mir'}}, 
'captured_at': '2024-05-22T04:59:17.787Z', 
'created_at': '2024-05-22T04:58:37.278Z', 
'test': True, 
'refunded_amount': {'value': '0.00', 'currency': 'RUB'}, 
'paid': True, 
'refundable': True, 
'receipt_registration': 'succeeded', 
'metadata': {'orderNumber': '10'}, 
'authorization_details': {'rrn': '793061212383108', 
'auth_code': '436896', 
'three_d_secure': {'applied': False, 'method_completed': False, 'challenge_completed': False}}}}
"""