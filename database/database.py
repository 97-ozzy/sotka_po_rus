import asyncpg
import random

DB_CONFIG = {
    "user": "postgres",
    "password": "your_password",
    "database": "egeshnik",
    "host": "localhost"
}

cache = {}

async def get_pool():
    return await asyncpg.create_pool(**DB_CONFIG)

async def load_task(pool, task_number: int):
    if task_number in cache:
        return random.choice(cache[task_number])

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT options, correct_answer FROM questions WHERE task_number = $1",
            task_number
        )

        if not rows:
            return None


        cache[task_number] = [(row['options'], row['correct_answer']) for row in rows]
        return random.choice(cache[task_number])
