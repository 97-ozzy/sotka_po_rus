import asyncio

import csv
import tempfile
import os
import shutil

from database.database import get_pool


async def update_explanations(csv_file_path: str, task_number):
    # Get the database connection pool
    pool = await get_pool()

    async with pool.acquire() as conn:
        # Read CSV file
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header if exists

            for row in reader:
                wrong_answer, correct_answer, question, word, explanation =row

                # Check if word exists in     questions_test table
                existing = await conn.fetchrow(
                    "SELECT word FROM     questions_test WHERE word = $1 and task_number = $2", word, task_number
                )

                if existing:
                    # Update explanation if word exists
                    pass
                    # await conn.execute(
                    #     """
                    #     UPDATE     questions_test 
                    #     SET wrong_answer = $1
                    #     WHERE word = $2 and task_number = $3
                    #     """,
                    #     wrong_answer, word, task_number
                    # )
                else:
                    # Insert new record if word doesn't exist
                    await conn.execute(
                        """
                        INSERT INTO     questions_test (
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





async def check_spelling(csv_file_path: str):
    # Создаем временный файл для записи исправленных данных
    temp_file_path = tempfile.mktemp(suffix='.csv')

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file, \
                open(temp_file_path, 'w', encoding='utf-8', newline='') as temp_file:

            reader = csv.reader(file)
            writer = csv.writer(temp_file)

            # Читаем и записываем заголовок (если есть)
            headers = next(reader, None)
            if headers:
                writer.writerow(headers)

            for row in reader:
                if len(row) < 5:  # Проверяем, что в строке достаточно элементов
                    writer.writerow(row)
                    continue

                wrong_answer, correct_answer, question, word, explanation = row[:5]
                
                
                task_number = 9  # Похоже, это константа в вашем коде
                # if correct_answer == 'а' and wrong_answer != 'о':
                #     wrong_answer = 'о'
                # if correct_answer == 'о' and wrong_answer != 'а':
                #     wrong_answer = 'а'
                #
                #
                # if correct_answer == 'и':
                #     if wrong_answer=='е' or wrong_answer=='ы':
                #         pass
                #     else:
                #         print(word)
                # if correct_answer == 'а' or correct_answer == 'о':
                #     if wrong_answer=='а' or wrong_answer=='о':
                #         pass
                #     else:
                #         print(word)

                        
                # Приводим к нижнему регистру, если не задача 4
                correct_answer = correct_answer.lower() if task_number != 4 else correct_answer
                wrong_answer = wrong_answer.lower() if task_number != 4 else wrong_answer
                if correct_answer == wrong_answer:
                    print(f'Ответы должны различаться {word}')
                # Проверяем соответствие слова и вопроса
                if word != question.replace('..', correct_answer):
                    if word == question.replace('..', wrong_answer):
                        # Меняем местами wrong и correct answer
                        wrong_answer, correct_answer = correct_answer, wrong_answer
                    else:
                        print(f"Несоответствие для строки: {word}")

                # Записываем исправленную строку
                writer.writerow([wrong_answer, correct_answer, question, word, explanation])

        # Заменяем исходный файл временным
        shutil.move(temp_file_path, csv_file_path)

    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        # Удаляем временный файл в случае ошибки
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise




async def main():
   #await update_explanations()
   #await update_task9_ng()
   await check_spelling('Untitled spreadsheet - Sheet1 (2).csv')
   pass


if __name__ == "__main__":
    asyncio.run(main())


