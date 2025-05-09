from datetime import datetime, timedelta, date
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
        premium_expires DATE DEFAULT CURRENT_DATE,
        submission_count INTEGER DEFAULT 0,
        registration_date DATE DEFAULT CURRENT_DATE,
        payment_method_id TEXT
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
            longest_streak INT DEFAULT 0,
            PRIMARY KEY (user_id, task_number)
    );''')
        await conn.execute('''
                CREATE TABLE weekly_stats (
    user_id BIGINT NOT NULL,
    task_number INTEGER NOT NULL,
    week_start DATE NOT NULL,
    attempts INTEGER DEFAULT 0,
    correct INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, task_number, week_start)
);''')
        await conn.execute('''
                CREATE TABLE IF NOT EXISTS payment_bills (
                    user_id BIGINT NOT NULL,
                    amount DECIMAL(5,2),
                    date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    payment_id TEXT UNIQUE,
                    PRIMARY KEY (payment_id)
            );''')


async def get_random_task(pool, task_number: int):
    if task_number in cache:
        return random.choice(cache[task_number])

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT word, question, correct_answer, wrong_answer FROM questions WHERE task_number = $1",
            task_number)
        if not rows:
            logger.error(f"No tasks found in db for task_number: {task_number}")
            return None

        cache[task_number] = [(row['word'], row['question'], row['correct_answer'], row['wrong_answer']) for row in rows]
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
            premium_expires_date = date.today() + timedelta(days=3)
            await conn.execute(
                "INSERT INTO users (user_id, username, premium, premium_expires_date) VALUES ($1, $2, $3, $4)",
                user_id, username, True, premium_expires_date
            )

async def submit_new_word(user_id, task_number, correct_word, wrong_word):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO word_submissions (user_id, task_number, correct_word, wrong_word)
            VALUES ($1, $2, $3, $4)
        ''', user_id, task_number, correct_word, wrong_word)



#------------------------------------------------------------------------
async def update_premium_status(user_id, is_true):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
                    UPDATE users
                    SET  premium=$1
                    WHERE user_id = $2
                ''', is_true, user_id)

async def update_premium_expiration(user_id, new_expiration):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
                        UPDATE users
                        SET  premium_expires_date=$1
                        WHERE user_id = $2
                    ''', new_expiration, user_id)

async def submit_first_recurring_payment_info(user_id, payment_method_id):
    user_id = int(user_id)
    pool = await get_pool()
    today = date.today()
    expire_date = today.replace(month=today.month + 1)
    async with pool.acquire() as conn:
        await conn.execute('''
                        UPDATE users
                        SET premium=TRUE, premium_expires_date = $1, payment_method_id = $2
                        WHERE user_id = $3
                    ''', expire_date, payment_method_id, user_id)

async def submit_payment(user_id, premium_price_rub, today, payment_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
                            INSERT INTO payment_bills (user_id, amount, date, payment_id)
                            VALUES ($1, $2, $3, $4)
                        ''', user_id, premium_price_rub, today, payment_id)

async def get_expiring_premium_users(current_date):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch('''
            SELECT user_id, payment_method_id 
            FROM users 
            WHERE premium_expires_date <= $1 AND payment_method_id = '-' AND premium = TRUE
                        ''', current_date)
        return rows


#-------------------------------------------------------------------------

def get_week_start(current_date: datetime = None) -> datetime.date:
    current_date = current_date or datetime.now()
    return (current_date - timedelta(days=current_date.weekday())).date()

def get_previous_week_start() -> datetime.date:
    return get_week_start(datetime.now() - timedelta(weeks=1))

#-----------------------------------------------------------------------
async def get_expiring_date(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        expiring_date = await conn.fetchval(
            "SELECT premium_expires_date FROM users WHERE user_id = $1", user_id
        )
    return expiring_date

async def get_nonactive_users(day_from, day_to):
    today = date.today()
    start_date = today - timedelta(days=day_from-1)
    end_date = today - timedelta(days=day_to)

    pool = await get_pool()
    async with pool.acquire() as conn:
        users = await conn.fetch(
            "SELECT user_id FROM users WHERE last_active <= $1 AND last_active >= $2",
            start_date,
            end_date
        )
    return users