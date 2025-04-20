import json
import asyncpg
import sqlite3
import asyncio

async def fill_db():
    # Подключение к базе данных
    conn = await asyncpg.connect(
        user='postgres',
        password='ozzy971',
        database='sotka_po_rus_tasks',
        host='localhost',  # Можно использовать "127.0.0.1" или "localhost"
        port=5432  # Порт по умолчанию
    )

    # Чтение JSON
    with open("../database/questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    for task_number, pairs in questions.items():
        for pair in pairs:
            correct = pair[0]
            options = pair

            await conn.execute('''
                INSERT INTO questions (task_number, answer_options, correct_answer)
                VALUES ($1, $2, $3)
            ''', int(task_number), options, correct)

    await conn.close()

 #asyncio.run(fill_db())

a ='dafs'
b='dfas'
print()