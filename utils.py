import csv
import asyncio

from database.database import get_pool


async def update_explanations(csv_file_path: str):
    # Get the database connection pool
    pool = await get_pool()

    async with pool.acquire() as conn:
        # Read CSV file
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header if exists

            for row in reader:
                task_number, wrong_answer, correct_answer, question, word, explanation =row

                task_number=int(task_number)
                # Check if word exists in questions table
                existing = await conn.fetchrow(
                    "SELECT word FROM questions WHERE word = $1 and task_number = $2", word, task_number
                )

                if existing:
                    # Update explanation if word exists
                    await conn.execute(
                        """
                        UPDATE questions 
                        SET explanation = $1 
                        WHERE word = $2 and task_number = $3
                        """,
                        explanation, word, task_number
                    )
                else:
                    # Insert new record if word doesn't exist
                    await conn.execute(
                        """
                        INSERT INTO questions (
                            task_number, 
                            wrong_answer, 
                            correct_answer, 
                            question, 
                            word, 
                            explanation
                        ) VALUES ($1, $2, $3, $4, $5, $6)
                        """,
                        task_number,
                        wrong_answer,
                        correct_answer,
                        question,
                        word,
                        explanation
                    )

                #print(f"Processed word: {word}")


async def update_task9_ng():
    # Get the database connection pool
    pool = await get_pool()

    async with pool.acquire() as conn:
        # Fetch rows where task_number = 9 and explanation contains '(НГ)'
        rows = await conn.fetch(
            """
            SELECT question, correct_answer, word 
            FROM questions 
            WHERE task_number = 9 AND explanation LIKE '%(НГ)%'
            """
        )

        # Update explanation for each matching row
        for row in rows:
            question = row['question']
            correct_answer = row['correct_answer']
            word = row['word']

            # Capitalize the correct_answer
            capitalized_answer = correct_answer.upper()

            # Replace '..' with the capitalized correct_answer in the question
            new_explanation = question.replace('..', capitalized_answer) + ' - словарное слово'

            await conn.execute(
                """
                UPDATE questions 
                SET explanation = $1 
                WHERE task_number = 9 AND word = $2
                """,
                new_explanation, word
            )
            print(f"Updated explanation for word '{word}': '{new_explanation}'")


async def main():
   #await update_explanations('utils/9_upd - 9_upd (копия) (1).csv')
   #await update_task9_ng()
   pass


if __name__ == "__main__":
    asyncio.run(main())

