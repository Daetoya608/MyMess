from PyQt5 import QtWidgets
from client.gui.authentication_interface import AuthenticationInterface

class AuthenticationWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = AuthenticationInterface()
        self.ui.setupUi(self)
        self.correct_checker_default = lambda s: len(s) > 0

    def get_input_data(self) -> dict:
        '''
        :return:
        {
            "username": str,
            "password": str,
        }
        '''
        result = dict()
        result["username"] = self.ui.username_line.text()
        result["password"] = self.ui.password_line.text()
        return result

    def is_correct_input_data(self):
        data = self.get_input_data()
        if not self.correct_checker_default(data["username"]):
            return False
        elif not self.correct_checker_default(data["password"]):
            return False
        return True



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    auth = AuthenticationWindow()
    auth.show()
    sys.exit(app.exec_())
