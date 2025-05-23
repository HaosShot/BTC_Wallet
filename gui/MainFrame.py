# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainFrame.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(600, 500)
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

        self.title_label = QtWidgets.QLabel(Form)
        self.title_label.setGeometry(QtCore.QRect(0, 20, 600, 60))
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setText("Ваш кошелек Bitcoin Testnet")
        self.title_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #6a5acd;")

        self.address_label = QtWidgets.QLabel(Form)
        self.address_label.setGeometry(QtCore.QRect(50, 100, 500, 30))
        self.address_label.setText("Адрес: Загрузка...")

        self.balance_label = QtWidgets.QLabel(Form)
        self.balance_label.setGeometry(QtCore.QRect(50, 140, 500, 30))
        self.balance_label.setText("Баланс: Загрузка...")

        self.receive_btn = QtWidgets.QPushButton(Form)
        self.receive_btn.setGeometry(QtCore.QRect(50, 220, 200, 50))
        self.receive_btn.setText("Получить BTC")

        self.send_btn = QtWidgets.QPushButton(Form)
        self.send_btn.setGeometry(QtCore.QRect(350, 220, 200, 50))
        self.send_btn.setText("Отправить BTC")

        self.new_address_btn = QtWidgets.QPushButton(Form)
        self.new_address_btn.setGeometry(QtCore.QRect(200, 300, 200, 50))
        self.new_address_btn.setText("Новый адрес")


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Title.setText(_translate("MainWindow", "Wallet"))
        self.Balance.setText(_translate("MainWindow", "Balance"))
        self.Btc_Adress.setText(_translate("MainWindow", "Adress"))
        self.Btc_PrivateKey.setText(_translate("MainWindow", "PrivateKey"))
        self.ReciveCoins.setText(_translate("MainWindow", "Получить монеты"))
        self.Send_Coins.setText(_translate("MainWindow", "Отправить"))
