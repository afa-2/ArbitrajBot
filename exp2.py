import configparser


config = configparser.ConfigParser()
config.read('config.ini')
publish_without_networks = bool(config.get('settings', 'publish_without_networks').strip())  # публиковать предложения, если нет совпадения по сетям

if publish_without_networks:
    print('publish_without_networks = True')