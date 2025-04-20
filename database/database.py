import asyncpg
import random
import sqlite3


def init_dbs():
    conn = sqlite3.connect("requests.db")
    cursor = conn.cursor()


    # Create submissions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS word_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        task_number INTEGER,
        correct_word TEXT,
        incorrect_words TEXT,
        status TEXT DEFAULT 'pending',
        submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                premium BOOLEAN DEFAULT FALSE,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
    conn.commit()
    conn.close()

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



def add_user_to_db(user_id: int):
    conn = sqlite3.connect("database/users.db")  # укажи имя своей базы
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            premium BOOLEAN DEFAULT FALSE
        )
    ''')

    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id)
        VALUES (?)
    ''', (user_id,))

    conn.commit()
    conn.close()
