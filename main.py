import sys

from PyQt5.QtWidgets import QApplication

from src.app import App

VERSION = "1.0.0"


def main() -> None:
    app = QApplication(sys.argv)
    main_window = App(VERSION)
    app.exec()


if __name__ == "__main__":
    main()
