from datetime import datetime

from PyQt5 import uic
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QIcon, QIntValidator, QRegExpValidator
from PyQt5.QtWidgets import QMainWindow

from src.enc import Enc
from src.utils import get_rel_path, warn_user


class App(QMainWindow):
    def __init__(self, version: str):
        super().__init__()
        self.version = version
        self.ui = None
        self.enc = Enc()
        self.load_ui()

    def load_ui(self):
        # Грузим UI из .ui файла
        self.ui = uic.loadUi(get_rel_path("app.ui"), self)

        # Размер окна
        self.ui.resize(600, 600)

        # Иконка окна
        self.ui.setWindowIcon(QIcon(get_rel_path("icon.ico")))

        # Название и версия в названии окна
        self.ui.setWindowTitle(f"Rippler v{self.version}")

        # Начальная страница
        self.open_encode_page()

        # Картинки, иконки
        self.ui.encode_page_btn.setIcon(QIcon(get_rel_path("encode.png")))
        self.ui.encode_run.setIcon(QIcon(get_rel_path("encode.png")))

        self.ui.decode_page_btn.setIcon(QIcon(get_rel_path("decode.png")))
        self.ui.decode_run.setIcon(QIcon(get_rel_path("decode.png")))

        self.ui.faq_page_btn.setIcon(QIcon(get_rel_path("faq.png")))

        # Кнопки
        self.ui.encode_page_btn.clicked.connect(self.open_encode_page)
        self.ui.decode_page_btn.clicked.connect(self.open_decode_page)
        self.ui.faq_page_btn.clicked.connect(self.open_faq_page)

        self.ui.encode_run.clicked.connect(self.run_encode)
        self.ui.decode_run.clicked.connect(self.run_decode)

        # Валидатор DDHH кода на странице дешифрования через regexp
        self.ui.decode_code.setValidator(QRegExpValidator(QRegExp(r"(0[1-9]|1[0-9]|2[0-9]|3[01])(0[0-9]|1[0-9]|2[0-3])")))

        # Валидатор модуля на странице шифрования
        self.ui.encode_module.setValidator(QIntValidator(1, 9999))

        # Модуль по умолчанию
        self.ui.encode_module.setText("128")

        # Показываем окно
        self.ui.show()

    # Обновляем DDHH код
    def update_ddtt_code(self):
        now = datetime.now()
        self.ui.encode_code.setText(f"{now.day:02}{now.hour:02}")

    # Открыть страницу шифрования
    def open_encode_page(self):
        self.update_ddtt_code()
        self.ui.stackedWidget.setCurrentIndex(0)

    # Открыть страницу дешифрования
    def open_decode_page(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    # Открыть страницу FAQ
    def open_faq_page(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    # Запуск шифрования
    def run_encode(self):
        self.update_ddtt_code()

        # Проверяем глупость юзера

        data = self.ui.encode_source_te.toPlainText().strip()
        if data == "":
            warn_user("Данные для шифрования отсутствуют")
            return

        code = int(self.ui.encode_code.text())

        module = self.ui.encode_module.text().strip()
        if module == "":
            warn_user("Пустой модуль")
            return

        module = int(module)
        if module == 0:
            warn_user("Модуль должен быть больше 0")
            return

        if module < 128:
            warn_user("При модуле меньше 128 возможны коллизии (разные символы могут дать одинаковый шифр)")

        result = []
        for line in data.split("\n"):
            line = line.strip()
            if line == "":
                continue

            encoded, err = self.enc.encode(line, code, module)
            if err:
                warn_user(f"Ошибка шифрования: {err}")
                return

            result.append(encoded)

        self.ui.encode_result_te.setText("\n".join(result))

    # Запуск дешифрования
    def run_decode(self):
        # Проверяем глупость юзера второй раз

        data = self.ui.decode_source_te.toPlainText().strip()
        if data == "":
            warn_user("Данные для дешифрования отсутствуют")
            return

        code = self.ui.decode_code.text()

        if code == "":
            warn_user("Пустой DDTT код")
            return

        if len(code) < 4:
            warn_user("Неполный DDTT код")
            return

        code = int(code)
        if code == 0:
            warn_user("DDTT код должен быть больше 0")
            return

        result = []
        for line in data.split("\n"):
            line = line.strip()
            if line == "":
                continue

            encoded, err = self.enc.decode(line, code)
            if err:
                warn_user(f"Ошибка дешифрования: {err}")
                return

            result.append(encoded)

        self.ui.decode_result_te.setText("\n".join(result))
