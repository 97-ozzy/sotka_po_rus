import logging
import asyncio
from datetime import datetime, date
from yookassa import Configuration, Payment

from config import PREMIUM_PRICE_RUB, RENEWAL_RETURN_URL, SHOP_ID, UKASSA_TOKEN
from database.database import get_expiring_premium_users, update_premium_status, submit_payment, update_premium_expiration

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка YooKassa
Configuration.account_id = SHOP_ID
Configuration.secret_key = UKASSA_TOKEN


async def create_recurring_payment(user_id: int, saved_payment_method_id: str = None):
    try:
        payment_params = {
            "amount": {
                "value": f"{PREMIUM_PRICE_RUB}.00",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": RENEWAL_RETURN_URL
            },
            "capture": True,
            "description": f"Автопродление премиум-подписки для пользователя {user_id}",
            "metadata": {
                "user_id": str(user_id),
                "is_recurring": "true"
            }
        }

        # Если есть сохраненный метод оплаты, используем его
        if saved_payment_method_id:
            payment_params["payment_method_id"] = saved_payment_method_id
        else:
            payment_params["save_payment_method"] = True

        payment = Payment.create(payment_params)
        logger.info(f"Создан платеж {payment.id} для пользователя {user_id}")
        return payment
    except Exception as e:
        logger.error(f"Ошибка при создании платежа для пользователя {user_id}: {e}")
        return payment.id

async def process_expiring_subscriptions():
    """Обрабатывает пользователей с истекающим сегодня премиумом."""
    today = date.today()
    expiring_users = await get_expiring_premium_users(today)

    if not expiring_users:
        logger.info("Нет пользователей с истекающим премиумом сегодня.")
        return

    for user in expiring_users:
        user_id = user["id"]
        saved_payment_method_id = user.get("saved_payment_method_id")  # Предполагается, что это поле хранится в БД
        logger.info(f"Обработка автопродления для пользователя {user_id}")

        payment = await create_recurring_payment(user_id, saved_payment_method_id)
        if not payment:
            continue

        # Проверка статуса платежа
        for _ in range(5):  # Проверяем до 5 раз с интервалом
            payment = Payment.find_one(payment.id)
            if payment.status == "succeeded":
                # Продлеваем премиум на месяц
                new_expiration = today.replace(month=today.month + 1)
                await update_premium_status(user_id, True)
                await update_premium_expiration(user_id, new_expiration)
                await submit_payment(user_id, PREMIUM_PRICE_RUB, payment.id)
                logger.info(f"Премиум продлен для пользователя {user_id} до {new_expiration}")
                break
            elif payment.status == "canceled":
                # Отключаем премиум, если платеж не прошел
                await update_premium_status(user_id, False)
                logger.warning(f"Платеж отменен для пользователя {user_id}, премиум отключен")
                break
            await asyncio.sleep(10)  # Ждем 10 секунд перед следующей проверкой
        else:
            logger.warning(f"Платеж {payment.id} для пользователя {user_id} не завершен вовремя")
            await update_premium_status(user_id, False)

async def main():
    """Основная функция для запуска скрипта."""
    logger.info(f"Запуск скрипта автоплатежей: {datetime.now()}")
    try:
        await process_expiring_subscriptions()
    except Exception as e:
        logger.error(f"Ошибка в основном цикле: {e}")
    logger.info("Скрипт автоплатежей завершен")

if __name__ == "__main__":
    asyncio.run(main())