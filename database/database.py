import asyncio
import os

import asyncpg
import random
from config import  DB_NAME, DB_USER, DB_PORT,DB_HOST, DB_PASSWORD, FLAG_FILE_PATH

cache ={}

async def clear_cache():
    global cache
    cache.clear()

async def check_cache_clear_flag():
    while True:
        if os.path.exists(FLAG_FILE_PATH):
            await clear_cache()
            os.remove(FLAG_FILE_PATH)
            print("Файл флаг очищен, кэш был очищен.")
        await asyncio.sleep(30)



_pool = None

async def get_pool():

    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT
        )

    return _pool



async def init_dbs():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        username TEXT,
        premium BOOLEAN DEFAULT FALSE,
        submission_count INTEGER DEFAULT 0,
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        premium_expires TEXT DEFAULT '0'
    );
""")
        await conn.execute('''
    CREATE TABLE IF NOT EXISTS word_submissions (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        task_number INTEGER,
        correct_word TEXT,
        wrong_words TEXT,
        status TEXT DEFAULT 'pending',
        submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS support_messages (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            message TEXT NOT NULL,
            date TIMESTAMP NOT NULL,
            is_viewed BOOLEAN DEFAULT FALSE
    );''')
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS user_task_stats (
            user_id BIGINT NOT NULL,
            username TEXT,
            task_number INT NOT NULL,
            total_attempts INT DEFAULT 0,
            correct_attempts INT DEFAULT 0,
            longest_streak INT DEFAULT 0,
            PRIMARY KEY (user_id, task_number)
    );''')



async def get_random_task(pool, task_number: int):
    if task_number in cache:
        return random.choice(cache[task_number])

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT question, correct_answer, wrong_answer FROM questions WHERE task_number = $1",
            task_number
        )

        if not rows:
            return None

        cache[task_number] = [(row['question'], row['correct_answer'], row['wrong_answer']) for row in rows]
        return random.choice(cache[task_number])


async def add_user_to_db(user_id: int, username: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        user_exists = await conn.fetchval(
            "SELECT 1 FROM users WHERE user_id = $1", user_id
        )
        if not user_exists:
            await conn.execute(
                "INSERT INTO users (user_id, username) VALUES ($1, $2)",
                user_id, username
            )

async def submit_new_word(user_id, task_number, correct_word, wrong_word):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO word_submissions (user_id, task_number, correct_word, wrong_word)
            VALUES ($1, $2, $3, $4)
        ''', user_id, task_number, correct_word, wrong_word)

async def get_pending_submission():
    pool = await get_pool()
    async with pool.acquire() as conn:
        row =  await conn.fetchrow('''
            SELECT id, user_id, task_number, correct_word, incorrect_words
            FROM word_submissions
            WHERE status = 'pending'
            ORDER BY submission_time ASC
            LIMIT 1
        ''')
        return row


async def approve_new_submission(user_id:int, sub_id:int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('UPDATE users SET submission_count = COALESCE(submission_count, 0) + 1 WHERE user_id = $1',user_id)
        await conn.execute("UPDATE word_submissions SET status = 'approved' WHERE id = $1", sub_id)

async def reject_new_submission(sub_id:int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('DELETE FROM word_submissions WHERE id = $1', sub_id)