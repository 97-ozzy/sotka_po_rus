from yookassa import Configuration, Payment

# Настройка с вашим ID магазина и секретным ключом
# Замените 'your_shop_id' и 'your_secret_key' на ваши реальные данные
Configuration.account_id = '1080022'
Configuration.secret_key = 'test_2rRoFU0aQ_TcGWpkqXG3VXrMzhgf8qzMGyi8IceADIU'

# Создание платежа на 20 рублей
payment = Payment.create({
    "amount": {
        "value": "20.00",  # Сумма в рублях
        "currency": "RUB"  # Валюта - российский рубль
    },
    "confirmation": {
        "type": "redirect",  # Тип подтверждения для генерации ссылки
        "return_url": "https://t.me/test_sotkapr_bot"  # URL для возврата после оплаты (замените на ваш)
    },
    "capture": True,  # Захват платежа сразу
    "save_payment_method": True,
    "description": "Оплата на 20 рублей"  # Описание платежа
})

# Получение и вывод ссылки для оплаты
payment_link = payment.confirmation.confirmation_url
print(payment_link)