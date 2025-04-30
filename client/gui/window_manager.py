from PyQt5.QtWidgets import QWidget
from .authentication_window import AuthenticationWindow
from .registration_window import RegistrationWindow
from .chat_main_window import ChatMainWindow
from .chat_create_dialog_window import ChatCreateDialogWindow
from PyQt5 import QtWidgets

class WindowManager:
    def __init__(self, container: QWidget):
        self.all_window = {
            "auth_window": AuthenticationWindow(),
            "reg_window": RegistrationWindow(),
            "chat_window": ChatMainWindow(),
            "create_chat_dialog": ChatCreateDialogWindow(),
        }
        self._container = container
        self._current_window = self.all_window["auth_window"]

        # Сразу добавляем первое окно
        self._container.layout().addWidget(self._current_window)

        # Подключаем кнопки
        self.all_window["auth_window"].ui.registration_button.clicked.connect(
            lambda: self.switch_to(self.all_window["reg_window"])
        )
        self.all_window["reg_window"].ui.authorization_button.clicked.connect(
            lambda: self.switch_to(self.all_window["auth_window"])
        )

        # self.all_window["chat_window"].ui.new_chat_button.clicked.connect(
        #     lambda: self.all_window["create_chat_dialog"].exec_()
        # )

    def switch_to(self, new_window: QWidget):
        if self._current_window is not None:
            self._current_window.setParent(None)

        self._current_window = new_window
        self._container.layout().addWidget(self._current_window)
        self._container.setFixedSize(self._current_window.size())



if __name__ == "__main__":
    from PyQt5.QtWidgets import QVBoxLayout
    import sys
    app = QtWidgets.QApplication(sys.argv)

    container = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    container.setLayout(layout)

    window_manager = WindowManager(container)
    container.setFixedSize(window_manager._current_window.size())
    container.show()

    sys.exit(app.exec_())
