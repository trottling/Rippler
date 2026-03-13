import os
import shutil
from datetime import datetime

from PyQt5 import uic
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QIcon, QIntValidator, QRegExpValidator
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow

from src.affine_enc import Affine
from src.huffman_enc import Huffman
from src.utils import get_rel_path, warn_user


class App(QMainWindow):
    def __init__(self, version: str):
        super().__init__()
        self.version = version
        self.ui = None
        self.affine_enc = Affine()
        self.huffman_enc = Huffman()
        self.huffman_encode_res = ""
        self.huffman_decode_res = ""
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
        self.open_faq_page()

        # Картинки
        self.ui.affine_encode_page_btn.setIcon(QIcon(get_rel_path("encode.png")))
        self.ui.affine_encode_run.setIcon(QIcon(get_rel_path("encode.png")))
        self.ui.affine_encode_code_copy.setIcon(QIcon(get_rel_path("copy.png")))
        self.ui.affine_encode_res_copy.setIcon(QIcon(get_rel_path("copy.png")))

        self.ui.affine_decode_page_btn.setIcon(QIcon(get_rel_path("decode.png")))
        self.ui.affine_decode_run.setIcon(QIcon(get_rel_path("decode.png")))
        self.ui.affine_decode_res_copy.setIcon(QIcon(get_rel_path("copy.png")))

        self.ui.huffman_encode_page_btn.setIcon(QIcon(get_rel_path("encode.png")))
        self.ui.huffman_encode_le_select.setIcon(QIcon(get_rel_path("file.png")))
        self.ui.huffman_encode_run.setIcon(QIcon(get_rel_path("zip.png")))
        self.ui.huffman_encode_save.setIcon(QIcon(get_rel_path("save.png")))

        self.ui.huffman_decode_page_btn.setIcon(QIcon(get_rel_path("decode.png")))
        self.ui.huffman_decode_le_select.setIcon(QIcon(get_rel_path("file.png")))
        self.ui.huffman_decode_run.setIcon(QIcon(get_rel_path("unzip.png")))
        self.ui.huffman_decode_save.setIcon(QIcon(get_rel_path("save.png")))

        self.ui.faq_page_btn.setIcon(QIcon(get_rel_path("faq.png")))

        # Кнопки

        # Navbar
        self.ui.affine_encode_page_btn.clicked.connect(self.open_affine_encode_page)
        self.ui.affine_decode_page_btn.clicked.connect(self.open_affine_decode_page)
        self.ui.huffman_encode_page_btn.clicked.connect(self.open_huffman_encode_page)
        self.ui.huffman_decode_page_btn.clicked.connect(self.open_huffman_decode_page)
        self.ui.faq_page_btn.clicked.connect(self.open_faq_page)

        # Affine encode
        self.ui.affine_encode_code_copy.clicked.connect(self.affine_copy_code)
        self.ui.affine_encode_res_copy.clicked.connect(self.affine_copy_encoded)
        self.ui.affine_encode_run.clicked.connect(self.affine_run_encode)

        # Affine decode
        self.ui.affine_decode_res_copy.clicked.connect(self.affine_copy_decoded)
        self.ui.affine_decode_run.clicked.connect(self.affine_run_decode)

        # Huffman encode
        self.ui.huffman_encode_run.clicked.connect(self.huffman_run_encode)
        self.ui.huffman_encode_le_select.clicked.connect(self.huffman_encode_select_file)
        self.ui.huffman_encode_save.clicked.connect(self.huffman_encode_save_file)
        self.ui.huffman_encode_save.setEnabled(False)

        # Huffman decode
        self.ui.huffman_decode_run.clicked.connect(self.huffman_run_decode)
        self.ui.huffman_decode_le_select.clicked.connect(self.huffman_decode_select_file)
        self.ui.huffman_decode_save.clicked.connect(self.huffman_decode_save_file)
        self.ui.huffman_decode_save.setEnabled(False)

        # Валидатор DDHH кода на странице affine дешифрования через regexp
        self.ui.affine_decode_code.setValidator(QRegExpValidator(QRegExp(r"(0[1-9]|1[0-9]|2[0-9]|3[01])(0[0-9]|1[0-9]|2[0-3])")))

        # Валидатор модуля на странице affine шифрования
        self.ui.affine_encode_module.setValidator(QIntValidator(1, 9999))

        # affine модуль по умолчанию
        self.ui.affine_encode_module.setText("128")

        # Показываем окно
        self.ui.show()

    # Обновляем affine DDHH код
    def update_ddtt_code(self):
        now = datetime.now()
        self.ui.affine_encode_code.setText(f"{now.day:02}{now.hour:02}")

    # Открыть страницу affine шифрования
    def open_affine_encode_page(self):
        self.update_ddtt_code()
        self.ui.stackedWidget.setCurrentIndex(0)

    # Открыть страницу affine дешифрования
    def open_affine_decode_page(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    # Открыть страницу huffman шифрования
    def open_huffman_encode_page(self):
        self.update_ddtt_code()
        self.ui.stackedWidget.setCurrentIndex(2)

    # Открыть страницу huffman дешифрования
    def open_huffman_decode_page(self):
        self.ui.stackedWidget.setCurrentIndex(3)

    # Открыть страницу FAQ
    def open_faq_page(self):
        self.ui.stackedWidget.setCurrentIndex(4)

    # Копирование из разных полей
    def affine_copy_encoded(self):
        text = self.ui.affine_encode_result_te.toPlainText().strip()
        if text != "":
            QApplication.clipboard().setText(text)

    def affine_copy_decoded(self):
        text = self.ui.affine_decode_result_te.toPlainText().strip()
        if text != "":
            QApplication.clipboard().setText(text)

    def affine_copy_code(self):
        text = self.ui.affine_encode_code.text().strip()
        if text != "":
            QApplication.clipboard().setText(text)

    # Выбор файла из проводника
    def huffman_encode_select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Текстовые файлы (*.txt *.md);;Все файлы (*)")
        if path:
            self.huffman_encode_le.setText(path)

    # Выбор файла из проводника
    def huffman_decode_select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Huffman файлы (*.huff);;Все файлы (*)")
        if path:
            self.huffman_decode_le.setText(path)

    def huffman_encode_save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "encoded.huff", "Huffman файлы (*.huff);;Все файлы (*)")
        if path == "":
            return

        shutil.move(self.huffman_encode_res, path)

    def huffman_decode_save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "decoded.txt", "TXT файлы (*.txt);;Все файлы (*)")
        if path == "":
            return

        shutil.move(self.huffman_decode_res, path)

    # Запуск шифрования
    def affine_run_encode(self):
        self.update_ddtt_code()

        # Проверяем глупость юзера

        data = self.ui.affine_encode_source_te.toPlainText().strip()
        if data == "":
            warn_user("Данные для шифрования отсутствуют")
            return

        code = int(self.ui.affine_encode_code.text())

        module = self.ui.affine_encode_module.text().strip()
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
        for line in data.replace(" ", "\n").split("\n"):
            line = line.strip()
            if line == "":
                continue

            encoded, err = self.affine_enc.encode(line, code, module)
            if err:
                warn_user(f"Ошибка шифрования: {err}")
                return

            result.append(encoded)

        self.ui.affine_encode_result_te.setText("\n".join(result))

    # Запуск дешифрования
    def affine_run_decode(self):
        # Проверяем глупость юзера второй раз

        data = self.ui.affine_decode_source_te.toPlainText().strip()
        if data == "":
            warn_user("Данные для дешифрования отсутствуют")
            return

        code = self.ui.affine_decode_code.text()

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

            encoded, err = self.affine_enc.decode(line, code)
            if err:
                warn_user(f"Ошибка дешифрования: {err}")
                return

            result.append(encoded)

        self.ui.affine_decode_result_te.setText("\n".join(result))

    # Запуск кодирования
    def huffman_run_encode(self):
        path = self.ui.huffman_encode_le.text().strip()
        if path == "":
            warn_user("Пустой путь")
            return

        if not os.path.exists(path):
            warn_user("Неправильный путь")
            return

        result, err = self.huffman_enc.encode_file(path)
        if err:
            warn_user(f"Ошибка кодирования: {err}")
            return

        self.huffman_encode_res = result

        self.ui.huffman_encode_save.setEnabled(True)

    # Запуск декодирования
    def huffman_run_decode(self):
        path = self.ui.huffman_decode_le.text().strip()
        if path == "":
            warn_user("Пустой путь")
            return

        if not os.path.exists(path):
            warn_user("Неправильный путь")
            return

        result, err = self.huffman_enc.decode_file(path)
        if err:
            warn_user(f"Ошибка декодирования: {err}")
            return

        self.huffman_decode_res = result
        self.ui.huffman_decode_save.setEnabled(True)
