

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 600)
        Form.setStyleSheet("""
            QWidget {
                background-color: #1b1b1b;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14pt;
            }
            QPushButton {
                background-color: #6a5acd;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7b68ee;
            }
            QPushButton:pressed {
                background-color: #483d8b;
            }
            QLabel {
                color: #cccccc;
            }
        """)

        self.Title = QtWidgets.QLabel(Form)
        self.Title.setGeometry(QtCore.QRect(0, 50, 400, 80))
        self.Title.setAlignment(QtCore.Qt.AlignCenter)
        self.Title.setWordWrap(True)
        self.Title.setStyleSheet("font-size: 28px; font-weight: bold; color: #6a5acd;")
        self.Title.setObjectName("Title")

        self.Register = QtWidgets.QPushButton(Form)
        self.Register.setGeometry(QtCore.QRect(100, 300, 200, 50))
        self.Register.setObjectName("Register")

        self.SignIn = QtWidgets.QPushButton(Form)
        self.SignIn.setGeometry(QtCore.QRect(100, 380, 200, 50))
        self.SignIn.setObjectName("SignIn")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)


    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.Title.setText(_translate("Form", "Wallet"))
        self.Register.setText(_translate("Form", "Регистрация"))
        self.SignIn.setText(_translate("Form", "Вход"))
