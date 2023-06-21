import configparser
dict_with_keys = {}
config = configparser.ConfigParser()
config.read('config.ini')
publish_without_networks = bool(config.get('settings', 'publish_without_networks').strip())  # публиковать предложения, если нет совпадения по сетям


print(publish_without_networks)
list = []
x = 5


if publish_without_networks == True or \
    (publish_without_networks == False and len(list) > 0):
    print('yes')