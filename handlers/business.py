from datetime import datetime
import json
from aiogram.types import Message
from loguru import logger

from utils.dispatcher import router
from utils.file_utils import save_data_to_json

# Глобальные словари для хранения состояния пользователей
notified_users = {}
answered_users = {}

@router.business_message()
async def handle_business_message(message: Message):
    """
    Обрабатывает сообщение от пользователя и проверяет рабочее время.
    Если рабочее время, бот отвечает, если нет - не отвечает.
    Также отвечает на запросы, связанные с паролем.
    """
    try:
        user_id = message.from_user.id
        user_data = {
            "user_id": user_id,
            "user_bot": message.from_user.is_bot,
            "user_first_name": message.from_user.first_name,
            "user_last_name": message.from_user.last_name,
            "user_username": message.from_user.username,
            "user_language_code": message.from_user.language_code,
            "user_is_premium": message.from_user.is_premium,
            "user_added_to_attachment_menu": message.from_user.added_to_attachment_menu,
            "user_can_join_groups": message.from_user.can_join_groups,
            "user_can_read_all_group_messages": message.from_user.can_read_all_group_messages,
            "user_supports_inline_queries": message.from_user.supports_inline_queries,
            "user_can_connect_to_business": message.from_user.can_connect_to_business,
            "user_has_main_web_app": message.from_user.has_main_web_app
        }

        # Логируем данные пользователя
        logger.info(f"Пользователь ID: {user_id}. Username: {message.from_user.username}, "
                    f"Фамилия: {message.from_user.last_name}, Имя: {message.from_user.first_name} написал сообщение.")

        file_path = f"data/{user_id}.json"

        # Сохраняем данные пользователя в JSON
        save_data_to_json(data=user_data, file_path=file_path)

        logger.info(f"Данные пользователя: {user_data} записаны или обновлены")

        # Проверка на наличие слова "пароль" в сообщении
        if "пароль" in message.text.lower():
            await message.reply(
                "Для получения пароля, пожалуйста, посетите моего помощника: [@h24service_bot](https://t.me/h24service_bot) 🤖.\n"
                "🔑 Чтобы получить пароль, необходимо подписаться на канал:\n"
                "[📲 Перейти к каналу](https://t.me/+uE6L_wey4c43YWEy) 📬.\n\n"
                "Спасибо за ваше сотрудничество! 🌟",
                parse_mode="Markdown"
            )
            return

        # Открываем файл и читаем данные рабочего времени
        with open('messages/working_hours.json', 'r') as file:
            data = json.load(file)

        # Получаем данные о начале и конце рабочего времени
        start_hour = int(data['start']['hour'])
        start_minute = int(data['start']['minute'])
        end_hour = int(data['end']['hour'])
        end_minute = int(data['end']['minute'])

        # Получаем текущее время
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute

        # Проверяем, является ли текущее время рабочим
        is_working_time = (
                (start_hour < current_hour < end_hour) or
                (current_hour == start_hour and current_minute >= start_minute) or
                (current_hour == end_hour and current_minute < end_minute)
        )

        if is_working_time:
            # Если рабочее время, очищаем информацию об уведомленных пользователях
            if user_id in notified_users:
                del notified_users[user_id]

            # Проверяем, отвечал ли бот уже пользователю в рабочее время
            if user_id not in answered_users:
                await message.reply(
                    "✅ **Сейчас рабочее время!**\n\n"
                    "🕐 Ваш запрос будет рассмотрен в ближайшее время. Пока я обрабатываю ваш вопрос, "
                    "приглашаю вас заглянуть на мой канал: "
                    "[📲 Откройте канал](https://t.me/+uE6L_wey4c43YWEy) 📬.\n\n"
                    "Спасибо за ваше терпение! 😊"
                , parse_mode="Markdown")
                # Сохраняем состояние пользователя, чтобы не отвечать повторно
                answered_users[user_id] = True
        else:
            # Проверяем, уведомляли ли мы пользователя ранее в нерабочее время
            if user_id not in notified_users:
                await message.reply(
                    "❌ **Сейчас нерабочее время!**\n\n"
                    "🌙 Пожалуйста, подождите до начала рабочего времени, и ваш запрос будет обработан. "
                    "Пока я не могу ответить, но вы можете ознакомиться с моим каналом: "
                    "[📲 Посетите канал](https://t.me/+uE6L_wey4c43YWEy) 📬.\n\n"
                    "Спасибо за ваше понимание и терпение! 🌟"
                , parse_mode="Markdown")
                # Сохраняем состояние пользователя для нерабочего времени
                notified_users[user_id] = True

            # Очищаем состояние для рабочего времени, чтобы бот снова мог ответить в рабочее время
            if user_id in answered_users:
                del answered_users[user_id]
    except Exception as e:
        logger.exception(f"Ошибка при обработке сообщения: {e}")

def register_handle_business_message():
    router.business_message.register(handle_business_message)

if __name__ == "__main__":
    register_handle_business_message()
