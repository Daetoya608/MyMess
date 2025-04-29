from .registration_interface import RegistrationInterface
from PyQt5 import QtWidgets

class RegistrationWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = RegistrationInterface()
        self.ui.setupUi(self)
        self.correct_checker_default = lambda s: len(s) > 0

    def get_input_data(self) -> dict:
        '''
        :return:
        {
            "email": str,
            "username": str,
            "password": str,
            "nickname": str
        }
        '''
        result = dict()
        result["email"] = self.ui.email_line.text()
        result["username"] = self.ui.username_line.text()
        result["password"] = self.ui.password_line.text()
        result["nickname"] = self.ui.nickname_line.text()
        return result

    def is_correct_input_data(self):
        data = self.get_input_data()
        if not self.correct_checker_default(data["email"]):
            return False
        elif not self.correct_checker_default(data["username"]):
            return False
        elif not self.correct_checker_default(data["password"]):
            return False
        elif not self.correct_checker_default(data["nickname"]):
            return False
        return True



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    reg = RegistrationWindow()
    reg.show()
    sys.exit(app.exec_())
