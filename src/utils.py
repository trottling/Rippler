import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox


# get_rel_path - функция, для резолвинга путей к ассетам при запуске кода или бинаркника
def get_rel_path(data_path: str, slash_replace: bool = True) -> str:
    if getattr(sys, "frozen", False):
        try:
            base_path = sys._MEIPASS  # type: ignore[attr-defined]
            result = os.path.join(base_path, data_path)
        except Exception:
            return ""
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        result = os.path.join(base_path, "", "..", "assets", data_path)

    return result.replace("\\", "/") if slash_replace else str(result)


def warn_user(text: str):
    msg = QMessageBox(None)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowIcon(QIcon(get_rel_path("icon.ico")))
    msg.setWindowTitle("Ошибка")
    msg.setText(text)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()
