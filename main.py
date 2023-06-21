import telebot
import configparser
import time
import logging
import datetime
from stock_exchanges.get_orders_from_exchanges import all_list_from_all_stock_market
from stock_exchanges.working_with_data import data_processing
from stock_exchanges.get_networks_for_transfer_coins import get_networks_for_transfer_coins


def _send_message(bot, chats_list, message):
    for chat in chats_list:
        if len(chat) > 0:
            bot.send_message(chat, message, parse_mode="HTML", disable_web_page_preview=True)


def main_script(first_message):
    try:
        # Настройки ---------------------------------------------------------------------------------------------------
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

        # mexc
        mexc_api_key = config.get('keys', 'mexc_api_key').strip()
        mexc_secret_key = config.get('keys', 'mexc_secret_key').strip()
        dict_with_keys['mexc'] = {'api_key': mexc_api_key, 'secret_key': mexc_secret_key}

        # gate
        gate_api_key = config.get('keys', 'gate_api_key').strip()
        gate_secret_key = config.get('keys', 'gate_secret_key').strip()
        dict_with_keys['gate'] = {'api_key': gate_api_key, 'secret_key': gate_secret_key}

        #  забираем настройки из ini
        # чаты
        chats = config.get('settings', 'chats').strip()
        chats_list = chats.strip('][').split(', ')

        min_profit_from_conf = float(config.get('settings', 'min_profit').strip())
        max_profit_from_conf = float(config.get('settings', 'max_profit').strip())
        min_profit_usd_from_conf = float(config.get('settings', 'min_profit_usd').strip())
        min_invest_conf = float(config.get('settings', 'min_invest').strip())
        max_invest_conf = float(config.get('settings', 'max_invest').strip())

        update_networks = float(config.get('settings', 'update_networks').strip())  # время обновления сетей
        publish_without_networks = bool(config.get('settings', 'publish_without_networks').strip())  # публиковать предложения, если нет совпадения по сетям

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

        # Логирование -------------------------------------------------------------------------------------------------
        logging.basicConfig(
            level=logging.INFO,  # Уровень логирования
            format='%(asctime)s [%(levelname)s] %(message)s',  # Формат сообщений
            handlers=[
                logging.FileHandler("my_log.log"),  # Запись логов в файл
            ]
        )

        # Другие переменные -------------------------------------------------------------------------------------------
        network_last_update = datetime.datetime.strptime('2023-01-10 18:26:47.204538', '%Y-%m-%d %H:%M:%S.%f')
        dict_with_networks = {'last_update': network_last_update}  # в словарь сразу отправляем тип datatime

        # Программа ---------------------------------------------------------------------------------------------------
        bot = telebot.TeleBot(api)  # запускаем бота

        # сообщение, что бот запущен
        logging.info(f'Бот запущен, {first_message}')
        _send_message(bot, chats_list, f"Бот запущен, {first_message}")
        text = f"Настройки:\n\n" \
               f"Количество монет: {len(currencies)}\n" \
               f"Минимальный спред: {min_profit_from_conf}%\n" \
               f"Максимальный спред: {max_profit_from_conf}%\n" \
               f"Минимальный профит {min_profit_usd_from_conf}$\n" \
               f"Минимальная сумма затрат на сделку: {min_invest_conf}$\n" \
               f"Максимальная сумма затрат на сделку: {max_invest_conf}$\n" \
               f"Интервал обновления сетей (в часах): {update_networks}"
        _send_message(bot, chats_list, text)

        while True:
            # раздел работы с сетями
            # проверяем когда последний раз обновлялись сети
            last_update = dict_with_networks['last_update']  # получаем время последнего обновления
            last_update_plus = last_update + datetime.timedelta(hours=update_networks)  # прибавляем часы из настройки
            now = datetime.datetime.now()  # узнаем сколько сейчас времени

            if now > last_update_plus:  # проверяем прошли ли с последнего обновления указанное кол-во часов
                start_time_update_networks = time.time()  # Засекаем время начала обновления сетей
                _send_message(bot, chats_list, "Обновление сетей")
                dict_with_networks = get_networks_for_transfer_coins(dict_with_keys, currencies)
                end_time_update_networks = time.time()  # Засекаем время окончания выполнения кода
                time_update_networks = end_time_update_networks - start_time_update_networks  # Вычисляем затраченное время
                _send_message(bot, chats_list, 'Сети обновлены')
                text = f'Сети обновлены. На это ушло {time_update_networks} секунд'
                logging.info(text)

            # работа с ордерами
            start_time = time.time()  # Засекаем время начала выполнения кода
            for currency in currencies:  # в отношении каждой валюты
                # получаем ордера с бирж. На этом этапе мы получаем просто список ордеров на продажу и ордер на покупку
                all_orders_from_all_exchanges = all_list_from_all_stock_market(currency)
                # обрабатываем сырые данные, находим выгодные предложения, считаем маржу,
                # формируем массив с релевантными данными
                all_orders = data_processing(all_orders_from_all_exchanges, dict_with_networks)

                if len(all_orders) > 0:  # если ордеров больше 0
                    previous_message = ''
                    for order in all_orders:  # в отношении каждого ордера
                        # переменные ---------------------------------------------
                        order_buy = order['order_buy'] # ордер на покупку
                        orders_sell = order['orders_sell']  # ордера на продажу
                        need_spent = order['need_spent']  # надо потратить
                        need_bought = order['need_bought'] # надо купить монет
                        profit = order['margin'] # профит в процентах
                        profit_in_dol = order['margin_in_dol']  # профит в долларах

                        name_exchange_where_buy = orders_sell[0][0]  # название биржи, где надо покупать монеты
                        name_exchange_where_sell = order_buy[0]  #  название биржи, где надо продавать монеты

                        # если профит больше минимального и надо потратить меньше максимального
                        if max_profit_from_conf >= profit >= min_profit_from_conf \
                                and max_invest_conf >= need_spent >= min_invest_conf \
                                and profit_in_dol >= min_profit_usd_from_conf:

                            # публикумем сообщение в телеграмм только в том слаче, если:
                            # 1. в настройках указано, что надо публиковать в том числе, если сетей нет
                            # 2. в настройках указано, что надо публиковать только если есть сети и сети есть
                            if publish_without_networks == True \
                                    or (publish_without_networks == False and len(order['matching_networks']) > 0):

                                # формируем спсок из всех ордеров на проаджу
                                text_orders_sell = ''
                                for order_sell in orders_sell:  # в отношении каждого ордера на продажу
                                    string = f'Цена: {order_sell[2]}, кол-во: {order_sell[3]}\n'
                                    text_orders_sell += string

                                # формируем сообщение
                                message = f"Пара: <b>{currency}/USDT</b>\n\n" \
                                          f"" \
                                          f"✅Покупка: <b><a href='{name_exchange_where_buy}'>{orders_sell[0][0]}</a></b>\n\n" \
                                          f"" \
                                          f"Выкупить объем: <b>{round(need_bought, 4)} {currency}</b>\n" \
                                          f"{text_orders_sell}" \
                                          f"Потратив <b>{round(need_spent, 2)} USDT</b>\n\n" \
                                          f"" \
                                          f"🔻Продажа: <b><a href='{name_exchange_where_sell}'>{order_buy[0]}</a></b>\n" \
                                          f"Продать: {order_buy[4]} {currency}\n" \
                                          f"По цене: {order_buy[3]} USDT\n\n" \
                                          f"" \
                                          f"📊 Спред: {profit}%\n" \
                                          f"💲 Профит: {profit_in_dol}$\n\n\n\n" \
                                          f"Для проверки:\n\n" \
                                          f"Все совпадающие сети: {order['matching_networks']}\n" \
                                          f"Самая выгодная сеть: {order['network_with_min_fee']}"

                                if message != previous_message:  # если сообщение не равно предыдущему
                                    _send_message(bot, chats_list, message)
                                previous_message = message  # сохраняем сообщение как предудщее, для проверки, что бы они не повторялись

            end_time = time.time()  # Засекаем время окончания выполнения кода
            elapsed_time = end_time - start_time  # Вычисляем затраченное время
            elapsed_time = round(elapsed_time, 2)

            text = f"Полный круг. Время выполнения кода: {elapsed_time} секунд"
            logging.info(text)

    except Exception as e:
        text_for_log = f"-------------------------------------------------------------\n" \
                       f"main_script упал\n" \
                       f"Ошибка: {e}\n" \
                       f"-------------------------------------------------------------"
        logging.error(text_for_log)
        time.sleep(30)
        main_script(f'Перезапуск после ошибки')


main_script('первый запуск')

#bot.infinity_polling()


