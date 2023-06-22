import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# валюты
currencies = config.get('settings', 'currencies').strip()
currencies = currencies.replace(" ", "")
currencies = currencies.replace("\n", "")
currencies = currencies.strip('][').split(',')

# черный список
currencies_black_list = config.get('settings', 'currencies_black_list').strip()
currencies_black_list = currencies_black_list.replace(" ", "")
currencies_black_list = currencies_black_list.replace("\n", "")
currencies_black_list = currencies_black_list.strip('][').split(',')

# формируем новый список из неповторяющихся валют и отстутвующих в черном списке
new_list = []
for currency in currencies:
    if currency not in new_list and currency not in currencies_black_list:
        new_list.append(currency)

currencies = new_list

print(len(new_list))