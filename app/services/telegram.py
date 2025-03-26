import aiohttp
from ..config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

async def send_salary_report(salary_data: dict) -> bool:
    """Отправка отчета о зарплате в Telegram"""
    # Форматируем месяц
    month_str = salary_data.get('month', '')
    if month_str:
        try:
            year, month = month_str.split('-')
            month_text = f"За {month}.{year}"
        except:
            month_text = "За текущий месяц"
    else:
        month_text = "За текущий месяц"

    # Форматируем сообщение
    message = f"""💰 *Зарплата модератора*
👤 {salary_data['role']} *{salary_data['nickname']}*
📅 {month_text}

*Статистика:*
• Онлайн: {salary_data['online_hours']} ч.
• Вопрос-ответ: {salary_data['questions']}
• Жалобы: {salary_data['complaints']}
• Строгие жалобы: {salary_data['severe_complaints']}
• Прикрепленные модераторы: {salary_data['attached_moderators']}
• Собеседования: {salary_data['interviews']}"""

    if salary_data.get('online_top'):
        message += f"\n• Топ онлайна: {salary_data['online_top']} место"
    if salary_data.get('questions_top'):
        message += f"\n• Топ вопросов: {salary_data['questions_top']} место"
    if salary_data.get('gma_review'):
        message += f"\n• Рецензия ГМА: {salary_data['gma_review']}"

    message += f"\n\n💎 *Итого: {salary_data['total_salary']} рубинов*"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return response.status == 200 