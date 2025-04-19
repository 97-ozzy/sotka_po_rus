import asyncpg
import random


cache = {}

_pool = None

async def get_pool():

    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            user='postgres',
            password='ozzy971',
            database='sotka_po_rus_tasks',
            host='localhost',  # Можно использовать "127.0.0.1" или "localhost"
            port=5432
        )
        print('dfsa')
    return _pool



async def load_task(pool, task_number: int):
    #print('asdf')
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

