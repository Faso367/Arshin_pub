import logging, os


class Logger(object):

    def __init__(self):
        self.logger = logging.getLogger('arshinAPIlogger')
        self.logger.setLevel(logging.INFO)  # уровень логирования DEBUG

        # Определение пути к файлу логирования
        script_directory = os.path.dirname(os.path.abspath(__file__))
        log_file_path = os.path.join(script_directory, 'logFiles\\arshinAPI.log')
        error_log_file_path = os.path.join(script_directory, 'logFiles\\arshinAPI_errors.log')

        # Создание обработчика для записи в файл
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.INFO)

        # Создание отдельного обработчика для записи ошибок в файл
        error_file_handler = logging.FileHandler(error_log_file_path)
        error_file_handler.setLevel(logging.ERROR)

        # Установка формата для обработчиков
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        error_file_handler.setFormatter(formatter)

        # Добавление обработчиков к логгеру
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_file_handler)