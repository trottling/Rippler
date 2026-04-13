import ctypes
import sys

from PySide6.QtWidgets import QApplication

from src.app import App


def main() -> None:
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Rippler.App")

    app = QApplication(sys.argv)
    main_window = App()
    app.exec()


if __name__ == "__main__":
    main()
