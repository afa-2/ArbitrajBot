import logging
import time

logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format='%(asctime)s [%(levelname)s] %(message)s',  # Формат сообщений
    handlers=[
        logging.FileHandler("my_log.log"),  # Запись логов в файл
    ]
)

for i in range(30):
    logging.info(i)
    print(i)
    time.sleep(1)