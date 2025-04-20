import asyncpg
import asyncio
from database.new_data import data15
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

# Получаем подключение к базе данных
async def get_pool():
    return await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT
    )

# Функция для вставки данных в таблицу
async def insert_words_data(data, task_number):
    pool = await get_pool()

    # Данные для вставки

    async with pool.acquire() as conn:
        # Вставка данных
        for group in data:
            for word_data in group:
                word = word_data[0]  # Правильное слово
                incorrect_words = word_data[1]  # Неверные варианты
                await conn.execute("""
                    INSERT INTO questions (task_number, correct_answer, answer_options) 
                    VALUES ($1, $2, $3)
                """, task_number, word, incorrect_words)

    print("Данные успешно вставлены!")

# Запуск скрипта
async def main():
    await insert_words_data()

if __name__ == "__main__":
    asyncio.run(main())
