import sys

from PyQt5.QtWidgets import QApplication

from src.app import App


def main() -> None:
    app = QApplication(sys.argv)
    main_window = App()
    app.exec()


if __name__ == "__main__":
    main()
