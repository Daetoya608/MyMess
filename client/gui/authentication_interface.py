# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/daetoya/files/authentication_interface.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class AuthenticationInterface(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1400, 1000)
        self.username_label = QtWidgets.QLabel(Form)
        self.username_label.setGeometry(QtCore.QRect(330, 350, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.username_label.setFont(font)
        self.username_label.setObjectName("username_label")
        self.exit_button = QtWidgets.QPushButton(Form)
        self.exit_button.setGeometry(QtCore.QRect(850, 870, 211, 61))
        self.exit_button.setObjectName("exit_button")
        self.password_line = QtWidgets.QLineEdit(Form)
        self.password_line.setGeometry(QtCore.QRect(510, 420, 511, 41))
        self.password_line.setObjectName("password_line")
        self.username_line = QtWidgets.QLineEdit(Form)
        self.username_line.setGeometry(QtCore.QRect(510, 350, 511, 41))
        self.username_line.setObjectName("username_line")
        self.password_label = QtWidgets.QLabel(Form)
        self.password_label.setGeometry(QtCore.QRect(340, 420, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.password_label.setFont(font)
        self.password_label.setObjectName("password_label")
        self.next_button = QtWidgets.QPushButton(Form)
        self.next_button.setGeometry(QtCore.QRect(1100, 870, 211, 61))
        self.next_button.setObjectName("next_button")
        self.authentication_label = QtWidgets.QLabel(Form)
        self.authentication_label.setGeometry(QtCore.QRect(550, 180, 410, 61))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.authentication_label.setFont(font)
        self.authentication_label.setObjectName("registration_label")
        self.registration_button = QtWidgets.QPushButton(Form)
        self.registration_button.setGeometry(QtCore.QRect(10, 20, 191, 41))
        self.registration_button.setObjectName("registration_button")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.username_label.setText(_translate("Form", "username:"))
        self.exit_button.setText(_translate("Form", "Выйти"))
        self.password_label.setText(_translate("Form", "password:"))
        self.next_button.setText(_translate("Form", "Далее"))
        self.authentication_label.setText(_translate("Form", "Аутентификация"))
        self.registration_button.setText(_translate("Form", "Регистрация"))
