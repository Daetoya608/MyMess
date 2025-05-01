from client.gui.chat_creating_default_interface import CreatingChatDialogDefault
from PyQt5 import QtWidgets
from client.gui.gui_types import MemberButton
from client.server_requests import get_user_by_username


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()
        else:
            # Рекурсивно очищаем вложенные лэйауты
            clear_layout(item.layout())


class ChatCreateDialogWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = CreatingChatDialogDefault()
        self.ui.setupUi(self)
        self.ui.add_members_button.clicked.connect(self.add_member_button)
        self.members_set = set()

        self.ui.cancel_button.clicked.connect(self.cancel_button_func)

    def cancel_button_func(self):
        self.reject()

    def clear_window(self):
        self.ui.chat_name_line.setText("")
        self.ui.members_line.setText("")
        self.members_set.clear()
        clear_layout(self.ui.added_members_horizontal_layout)

    def get_chat_name(self):
        line = self.ui.chat_name_line.text()
        return line

    def get_member(self):
        line = self.ui.members_line.text()
        return line

    def add_member_button_by_username(self, username_str):
        button = MemberButton(username_str)
        button.setGeometry(20, 20, 100, 30)
        button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.ui.added_members_horizontal_layout.addWidget(button)

    def add_member_button(self):
        member_username = self.get_member()
        if len(member_username) == 0: return
        user = get_user_by_username(member_username)
        if not user["status"] or user["user_id"] in self.members_set:
            return
        self.members_set.add(user["user_id"])
        self.add_member_button_by_username(member_username)

    def is_correct_input_data(self) -> bool:
        if len(self.get_chat_name()) > 0 and len(self.members_set) > 0:
            return True
        return False




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    wind = ChatCreateDialogWindow()
    wind.show()
    sys.exit(app.exec_())
