import time
from collections import defaultdict
from typing import Callable, Dict, Any, Awaitable, List # Добавили List
from aiogram import BaseMiddleware
from aiogram.types import Message # Работаем только с сообщениями

# Словарь для хранения времени последнего предупреждения для пользователя
# Его можно вынести в Redis или другую базу для персистентности
user_warning_timestamps: Dict[int, float] = {}

class AntiSpamMiddleware(BaseMiddleware): # Переименовано для ясности
    def __init__(self, limit: int = 7, time_window: int = 10, warning_cooldown: int = 60):
        """
        Middleware для ограничения частоты сообщений (анти-спам).

        :param limit: Максимальное количество сообщений.
        :param time_window: Временное окно в секундах для подсчета сообщений.
        :param warning_cooldown: Минимальный интервал в секундах между отправкой предупреждений одному пользователю.
        """
        # defaultdict(list) хранит список временных меток для каждого user_id
        self.user_message_timestamps: Dict[int, List[float]] = defaultdict(list)
        self.limit = limit
        self.time_window = time_window
        self.warning_cooldown = warning_cooldown
        # Глобальный словарь для времени предупреждений (или передать его в init)
        self.user_warning_timestamps = user_warning_timestamps

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], # Уточнили тип handler
        event: Message, # Явно указываем, что ждем Message
        data: Dict[str, Any],
    ) -> Any:
        # Проверка, что событие - это сообщение от пользователя (хотя регистрация на dp.message уже это подразумевает)
        if not isinstance(event, Message) or not event.from_user:
            # Если зарегистрировано на dp.update, эта проверка важна
            # Если на dp.message, она может быть избыточна
            return await handler(event, data) # Пропускаем другие типы событий

        user_id = event.from_user.id
        now = time.time()

        # 1. Получаем список временных меток пользователя
        timestamps = self.user_message_timestamps[user_id]

        # 2. Удаляем старые метки, которые вышли за пределы time_window
        # Создаем новый список только с валидными (свежими) метками
        valid_timestamps = [ts for ts in timestamps if now - ts < self.time_window]

        # 3. Добавляем время текущего сообщения
        valid_timestamps.append(now)

        # 4. Сохраняем обновленный список меток для пользователя
        self.user_message_timestamps[user_id] = valid_timestamps

        # 5. Проверяем, превышен ли лимит сообщений
        if len(valid_timestamps) > self.limit:
            # Лимит превышен - это спам!
            last_warning_time = self.user_warning_timestamps.get(user_id, 0)

            # 6. Проверяем, не отправляли ли предупреждение недавно
            if now - last_warning_time > self.warning_cooldown:
                # Обновляем время последнего предупреждения
                self.user_warning_timestamps[user_id] = now
                # Отправляем сообщение пользователю
                await event.answer(
                    f"❗️ Обнаружено слишком много сообщений!\n"
                    f"({len(valid_timestamps)} сообщ. за последние {self.time_window} сек).\n"
                    f"Пожалуйста, подождите. Следующее предупреждение не ранее чем через {self.warning_cooldown} сек."
                )
                # ВАЖНО: Останавливаем дальнейшую обработку этого сообщения
                return None # handler НЕ будет вызван

            else:
                # Предупреждение уже было недавно, просто игнорируем сообщение молча
                # Можно добавить тихое удаление сообщения, если бот - админ
                # try:
                #    await event.delete()
                # except Exception: pass # Игнорируем ошибки удаления
                return None # handler НЕ будет вызван

        # 7. Если лимит не превышен, продолжаем выполнение и вызываем следующий хендлер
        return await handler(event, data)