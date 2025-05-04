import datetime
import logging
from asyncio import exceptions
from io import BytesIO
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from database.database import get_pool, get_premium_users, get_week_start, get_previous_week_start
from handlers.base import menu
from keyboards.inline_kb import menu_and_buy_premium, period_selection_keyboard

router = Router()


@router.callback_query(F.data == 'stats')
async def user_stats(callback: CallbackQuery):
    await callback.answer()
    premium_users = await get_premium_users()
    if callback.from_user.id not in premium_users:
        await callback.message.edit_text('Личная статистика доступна только премиум пользователям',
                                      reply_markup=menu_and_buy_premium())
        await callback.answer()
        return

    try:
        await callback.message.edit_text("Выберите период для просмотра статистики:",
                                      reply_markup=period_selection_keyboard())
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            # Message is already correct, no need to edit
            pass


@router.callback_query(F.data == 'period_all')
async def handle_period_all(callback: CallbackQuery):
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Получаем агрегированную статистику за все время из weekly_stats
        rows = await conn.fetch(
            '''
            SELECT 
                task_number,
                SUM(attempts) as total_attempts,
                SUM(correct) as total_correct
            FROM weekly_stats
            WHERE user_id = $1
            GROUP BY task_number
            ORDER BY task_number;
            ''',
            callback.from_user.id
        )

    if not rows:
        await callback.message.answer("У вас пока нет статистики за любой период.")
        return

    text = "📊 Ваша статистика за все время:\n\n"
    for row in rows:
        task_number = row["task_number"]
        total = row["total_attempts"]
        correct = row["total_correct"]
        accuracy = (correct / total) * 100 if total else 0

        text += (
            f"➤ Задание №{task_number}:\n"
            f"  • Всего попыток: {total}\n"
            f"  • Верных решений: {correct}\n"
            f"  • Точность: {accuracy:.1f}%\n\n"
        )

    try:
        await callback.message.edit_text(text)
        await menu(callback.message)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
                # Message is already correct, no need to edit
            pass

@router.callback_query(F.data == 'period_current')
async def handle_period_current(callback: CallbackQuery):
    await show_weekly_stats(callback, get_week_start())

@router.callback_query(F.data == 'period_previous')
async def handle_period_previous(callback: CallbackQuery):
    await show_weekly_stats(callback, get_previous_week_start())


async def show_weekly_stats(context: CallbackQuery | Message, week_start: datetime.date):
    if isinstance(context, CallbackQuery):
        message = context.message
        user_id = context.from_user.id
    else:
        message = context
        user_id = context.from_user.id
    week_end = week_start + datetime.timedelta(days=6)
    week_start_str = week_start.strftime("%d.%m.%y")
    week_end_str = week_end.strftime("%d.%m.%y")
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            '''
            SELECT task_number, attempts, correct
            FROM weekly_stats
            WHERE user_id = $1 AND week_start = $2
            ORDER BY task_number;
            ''',
            user_id, week_start
        )

    if not rows:
        await message.edit_text(f"Нет данных c *{week_start_str}* по *{week_end_str}*", parse_mode='Markdown')
        await menu(message)
        return

    text = f"📊 Статистика c *{week_start_str}* по *{week_end_str}*:\n\n"
    for row in rows:
        accuracy = (row['correct'] / row['attempts']) * 100 if row['attempts'] else 0
        text += f"№{row['task_number']}: {row['attempts']} попыток, {row['correct']} верно ({accuracy:.1f}%)\n\n"


    try:
        await message.edit_text(text, parse_mode='Markdown')
        await menu(message)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            # Message is already correct, no need to edit
            pass


from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4, landscape

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont




@router.callback_query(F.data == 'period_pdf')
async def handle_period_pdf(callback: CallbackQuery):
    try:
        await callback.message.edit_text("Генерируем PDF-отчёт...")
    except exceptions.TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass

    user_id = callback.from_user.id
    username = callback.from_user.username or str(user_id)  # Fallback to user_id if username is None
    pool = await get_pool()

    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                '''
                SELECT task_number, week_start, attempts, correct
                FROM weekly_stats
                WHERE user_id = $1
                ORDER BY week_start, task_number;
                ''',
                user_id
            )

        if not rows:
            await callback.message.answer("У вас пока нет статистики для генерации отчёта.")
            return

        # Собираем данные в структуру
        data_dict = {}
        weeks = set()
        tasks = set()

        for row in rows:
            task = row['task_number']
            week = row['week_start']  # Store as datetime for sorting
            accuracy = (row['correct'] / row['attempts']) * 100 if row['attempts'] else 0

            if task not in data_dict:
                data_dict[task] = {}
            data_dict[task][week] = f"{accuracy:.1f}%"

            weeks.add(week)
            tasks.add(task)

        # Сортируем недели и создаем метки с номерами
        sorted_weeks = sorted(weeks)
        week_labels = [f"{i+1} неделя" for i in range(len(sorted_weeks))]
        logging.info(f"Assigned week labels: {week_labels}")

        # Сортируем задания
        sorted_tasks = sorted(tasks)

        # Создаем матрицу данных
        matrix = []
        # Заголовок таблицы
        header = ["Задание"] + week_labels
        matrix.append(header)

        for task in sorted_tasks:
            row = [str(task)]
            for week in sorted_weeks:
                row.append(data_dict.get(task, {}).get(week, "-"))
            matrix.append(row)

        # Регистрация шрифта с поддержкой кириллицы
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
            logging.info("Fonts DejaVuSans and DejaVuSans-Bold registered successfully")
        except Exception as e:
            logging.error(f"Failed to register fonts: {e}")
            await callback.message.answer("Ошибка при загрузке шрифтов. Попробуйте позже.")
            return

        # Генерация PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            title=f"Статистика_{user_id}",
            encoding='utf-8'
        )

        elements = []
        styles = getSampleStyleSheet()

        # Настройка стиля Title для поддержки кириллицы
        styles['Title'].fontName = 'DejaVuSans-Bold'
        styles['Title'].fontSize = 14
        styles['Title'].leading = 16
        logging.info(f"Title style set to font: {styles['Title'].fontName}")

        # Заголовок
        title = Paragraph(f"Статистика решений пользователя {username}", styles['Title'])
        elements.append(title)

        # Создаем таблицу
        table = Table(matrix, colWidths=[50] + [60] * len(sorted_weeks))
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ])

        # Добавляем чередующиеся цвета строк
        for i in range(1, len(matrix), 2):
            style.add('BACKGROUND', (0, i), (-1, i), colors.lightblue)

        table.setStyle(style)
        elements.append(table)

        # Собираем документ
        doc.build(elements)

        # Отправка PDF
        buffer.seek(0)
        pdf_file = BufferedInputFile(buffer.read(), filename=f"table_stat_{user_id}.pdf")

        try:

            await callback.message.answer_document(
                document=pdf_file,
                caption="Табличная статистика по заданиям и неделям"
            )
            await menu(callback.message)
        except exceptions.TelegramBadRequest as e:
            if "message is not modified" in str(e):
                pass
            else:
                logging.error(f"Telegram API error: {e}")
                await callback.message.answer("Ошибка при отправке отчёта. Попробуйте позже.")

    except Exception as e:
        logging.error(f"PDF generation error: {e}")
        await callback.message.answer("Ошибка при генерации отчёта. Попробуйте позже.")

    finally:
        buffer.close()
