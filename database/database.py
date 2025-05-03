import datetime
import time
import logging
import asyncpg
import random
from config import  DB_NAME, DB_USER, DB_PORT,DB_HOST, DB_PASSWORD

logger = logging.getLogger(__name__)

cache ={}
premium_users_cache = []

async def clear_cache():
    global cache
    global premium_users_cache
    cache.clear()
    premium_users_cache.clear()




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
        username TEXT DEFAULT '-',
        last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        premium BOOLEAN DEFAULT FALSE,
        premium_expires TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        submission_count INTEGER DEFAULT 0,
        registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
""")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                username TEXT DEFAULT '-',
                is_viewed BOOLEAN DEFAULT FALSE,
                file TEXT,
                time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
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
        submission_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    ''')
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS support_messages (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            username TEXT DEFAULT '-'
            message TEXT NOT NULL,
            date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
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
            "SELECT id, question, correct_answer, wrong_answer FROM questions WHERE task_number = $1",
            task_number)
        if not rows:
            logger.error(f"No tasks found in db for task_number: {task_number}")
            return None

        cache[task_number] = [(row['id'], row['question'], row['correct_answer'], row['wrong_answer']) for row in rows]
        return random.choice(cache[task_number])



async def get_premium_users():
    global premium_users_cache
    if len(premium_users_cache)==0:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT user_id FROM users WHERE  premium = TRUE"
            )
        premium_users_cache = [ int(row['user_id']) for row in rows]

    return premium_users_cache

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

async def submit_payment(user_id,username, file):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO subscriptions (user_id, username, file)
            VALUES ($1, $2, $3)
        ''', user_id, username, file)



async def get_pending_premium():
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow('''
                SELECT id, user_id, username, file, time
                FROM subscriptions
                WHERE is_viewed = FALSE
                ORDER BY time DESC
                LIMIT 1
            ''')
        return row

async def set_premium_status(sub_id, user_id):
    pool = await get_pool()
    current_datetime = datetime.datetime.now()
    time_delta = datetime.timedelta(days=30)
    expire_date = current_datetime + time_delta
    async with pool.acquire() as conn:
        await conn.execute('''
                    UPDATE users
                    SET premium=TRUE, premium_expires_date = $1
                    WHERE user_id = $2
                ''', expire_date, user_id)
        await conn.execute(
            '''
            UPDATE subscriptions
            SET is_viewed = TRUE
            WHERE id = $1
            ''', sub_id)


async def remove_bill_from_db(sub_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
                    DELETE FROM subscriptions
            WHERE id = $1
                ''', sub_id)

