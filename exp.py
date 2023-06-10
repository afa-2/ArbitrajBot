import telebot
import configparser
import time
import logging
from stock_exchanges.working_with_data import get_orders_from_exchanges


def _send_message(bot, chats_list, message):
    for chat in chats_list:
        if len(chat) > 0:
            bot.send_message(chat, message, parse_mode="HTML", disable_web_page_preview=True)


# Настройки --------------------------------------------------------------------------------------------------------
# забираем ключи из ini
dict_with_keys = {}
config = configparser.ConfigParser()
config.read('config.ini')

# telegram
api = config.get('keys', 'api_key').strip()

# bybit
bybit_api_key = config.get('keys', 'bybit_api_key').strip()
bybit_secret_key = config.get('keys', 'bybit_secret_key').strip()
dict_with_keys['bybit'] = {'api_key': bybit_api_key, 'secret_key': bybit_secret_key}

#  забираем настройки из ini
# чаты
chats = config.get('settings', 'chats').strip()
chats_list = chats.strip('][').split(', ')

min_profit_from_conf = float(config.get('settings', 'min_profit').strip())
max_profit_from_conf = float(config.get('settings', 'max_profit').strip())
min_profit_usd_from_conf = float(config.get('settings', 'min_profit_usd').strip())
max_invest_conf = float(config.get('settings', 'max_invest').strip())

# валюты
currencies = config.get('settings', 'currencies').strip()
currencies = currencies.replace(" ", "")
currencies = currencies.replace("\n", "")
currencies = currencies.strip('][').split(',')
# удаляем повторяющиеся валюты
new_list = []
for currency in currencies:
    if currency not in new_list:
        new_list.append(currency)

currencies = new_list

# Логирование ------------------------------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format='%(asctime)s [%(levelname)s] %(message)s',  # Формат сообщений
    handlers=[
        logging.FileHandler("my_log.log"),  # Запись логов в файл
    ]
)

# Программа --------------------------------------------------------------------------------------------------------
bot = telebot.TeleBot(api)  # запускаем бота

# сообщение, что бот запущен
_send_message(bot, chats_list, f"Бот запущен")


@bot.message_handler(content_types=['text'])
def send_menu(message):
    """
    Слушает сообщения и на любое сообщение отправляет меню.
    """
    user_name = message.from_user.username

    text = f"ID: {message.chat.id}"
    bot.send_message(message.chat.id, text)


    # если это общий чат


bot.infinity_polling()





