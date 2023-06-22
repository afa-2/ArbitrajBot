import json

def _send_message(bot, chats_list, message):
    for chat in chats_list:
        if len(chat) > 0:
            bot.send_message(chat, message, parse_mode="HTML", disable_web_page_preview=True)


def _save_networks_to_file(dict_with_networks):
    file_path = 'networks.json'
    with open(file_path, 'w') as f:
        json.dump(dict_with_networks, f)


dict = {'one': 1, 'two': 2}

_save_networks_to_file(dict)