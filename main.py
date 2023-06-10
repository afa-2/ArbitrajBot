import telebot
import configparser
import time
import logging
from stock_exchanges.working_with_data import get_orders_from_exchanges


def _send_message(bot, chats_list, message):
    for chat in chats_list:
        if len(chat) > 0:
            bot.send_message(chat, message, parse_mode="HTML", disable_web_page_preview=True)


def main_script(first_message):
    try:
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
        min_invest_conf = float(config.get('settings', 'min_invest').strip())
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
        _send_message(bot, chats_list, f"Бот запущен, {first_message}")
        text = f"Настройки:\n\n" \
               f"Количество монет: {len(currencies)}\n" \
               f"Минимальный спред: {min_profit_from_conf}%\n" \
               f"Максимальный спред: {max_profit_from_conf}%\n" \
               f"Минимальный профит {min_profit_usd_from_conf}$\n" \
               f"Минимальная сумма затрат на сделку: {min_invest_conf}$\n" \
               f"Максимальная сумма затрат на сделку: {max_invest_conf}$\n" \

        _send_message(bot, chats_list, text)

        while True:
            try:
                start_time = time.time()  # Засекаем время начала выполнения кода
                for currency in currencies:  # в отношении каждой валюты
                    all_orders = get_orders_from_exchanges(currency)  # получаем все ордера
                    if len(all_orders) > 0:  # если ордеров больше 0
                        previous_message = ''
                        for order in all_orders:  # в отношении каждого ордера
                            order_buy = order['order_buy'] # ордер на покупку
                            orders_sell = order['orders_sell']  # ордера на продажу
                            need_spent = order['need_spent']  # надо потратить
                            need_bought = order['need_bought'] # надо купить монет
                            profit = order['margin'] # профит в процентах
                            profit_in_dol = order['margin_in_dol']  # профит в долларах

                            # если профит больше минимального и надо потратить меньше максимального
                            if max_profit_from_conf >= profit >= min_profit_from_conf \
                                    and max_invest_conf >= need_spent >= min_invest_conf \
                                    and profit_in_dol >= min_profit_usd_from_conf:

                                # формируем спсок из всех ордеров на проаджу
                                text_orders_sell = ''
                                for order_sell in orders_sell:  # в отношении каждого ордера на продажу
                                    string = f'Цена: {order_sell[2]}, кол-во: {order_sell[3]}\n'
                                    text_orders_sell += string

                                # формируем сообщение
                                message = f"Пара: <b>{currency}/USDT</b>\n\n" \
                                          f"" \
                                          f"✅Покупка: <b><a href='{orders_sell[0][1]}'>{orders_sell[0][0]}</a></b>\n\n" \
                                          f"" \
                                          f"Выкупить объем: <b>{round(need_bought, 4)} {currency}</b>\n" \
                                          f"{text_orders_sell}" \
                                          f"Потратив <b>{round(need_spent, 2)} USDT</b>\n\n" \
                                          f"" \
                                          f"🔻Продажа: <b><a href='{order_buy[1]}'>{order_buy[0]}</a></b>\n" \
                                          f"Продать: {order_buy[4]} {currency}\n" \
                                          f"По цене: {order_buy[3]} USDT\n\n" \
                                          f"" \
                                          f"📊 Спред: {profit}%\n" \
                                          f"💲 Профит: {profit_in_dol}$"

                                if message != previous_message:  # если сообщение не равно предыдущему
                                    _send_message(bot, chats_list, message)
                                previous_message = message  # сохраняем сообщение как предудщее, для проверки, что бы они не повторялись

                end_time = time.time()  # Засекаем время окончания выполнения кода
                elapsed_time = end_time - start_time  # Вычисляем затраченное время
                elapsed_time = round(elapsed_time, 2)

                text = f"Полный круг. Время выполнения кода: {elapsed_time} секунд"
                logging.info(text)

            except Exception as e:
                logging.error(e)
                _send_message(bot, chats_list, "Упс. Какая-то ошибочка на самом верхнем уровне")

    except Exception as e:
        text_for_log = f"-------------------------------------------------------------" \
                       f"Бот упал" \
                       f"Ошибка: {e}" \
                       f"-------------------------------------------------------------"
        logging.error(text_for_log)
        time.sleep(30)
        main_script(f'перезапуск после ошибки: {str(e)}')


main_script('первый запуск')

#bot.infinity_polling()


