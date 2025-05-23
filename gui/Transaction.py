# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Transaction.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(300, 500)
        Form.setStyleSheet("QWidget {\n"
"    background-color: #000000;\n"
"    color: #FFFFFF;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"    font-size: 24pt;\n"
"   \n"
"    box-shadow: 0 0 30px rgba(255, 255, 255, 0.1);\n"
"}\n"
"\n"
"/* Специальные метки (Balance, Btc_Address, Btc_PrivateKey) */\n"
"QLabel#Btc_Adress, QLabel#Balance, QLabel#Btc_PrivateKey {\n"
"    font-size: 10pt;\n"
"    color: #FFFFFF;\n"
"}\n"
"\n"
"/* Кнопки */\n"
"QPushButton {\n"
"    background-color: #FFFFFF;\n"
"    color: #000000;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    padding: 5px 10px;\n"
"    font-size: 10pt;\n"
"    transition: all 0.3s ease;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #DDDDDD;\n"
"    border: 2px solid #FFFFFF;\n"
"    box-shadow: 0 0 10px #FFFFFF;\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: #BBBBBB;\n"
"}\n"
"\n"
"/* Поля ввода текста */\n"
"QLineEdit, QTextEdit {\n"
"    background-color: #FFFFFF;\n"
"    color: #000000;\n"
"    border: none;\n"
"    border-radius: 4px;\n"
"    padding: 4px;\n"
"    selection-background-color: #AAAAAA;\n"
"    font-size: 10pt;\n"
"}\n"
"\n"
"/* Метки */\n"
"QLabel {\n"
"    color: #FFFFFF;\n"
"}\n"
"\n"
"/* Выпадающие списки */\n"
"QComboBox {\n"
"    background-color: #FFFFFF;\n"
"    color: #000000;\n"
"    border: none;\n"
"    border-radius: 4px;\n"
"    padding: 4px;\n"
"}\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #FFFFFF;\n"
"    color: #000000;\n"
"    selection-background-color: #AAAAAA;\n"
"}\n"
"\n"
"/* Чекбоксы */\n"
"QCheckBox {\n"
"    spacing: 5px;\n"
"    color: #FFFFFF;\n"
"}\n"
"QCheckBox::indicator {\n"
"    width: 16px;\n"
"    height: 16px;\n"
"}\n"
"QCheckBox::indicator:unchecked {\n"
"    border: 1px solid #FFFFFF;\n"
"    background: #000000;\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"    border: 1px solid #FFFFFF;\n"
"    background: #FFFFFF;\n"
"}\n"
"\n"
"/* Скроллбары */\n"
"QScrollBar:vertical, QScrollBar:horizontal {\n"
"    background: #000000;\n"
"    width: 10px;\n"
"}\n"
"QScrollBar::handle:vertical, QScrollBar::handle:horizontal {\n"
"    background: #FFFFFF;\n"
"    min-height: 20px;\n"
"    border-radius: 4px;\n"
"}\n"
"QScrollBar::handle:hover {\n"
"    background: #AAAAAA;\n"
"}\n"
"\n"
"/* Групповые боксы */\n"
"QGroupBox {\n"
"    border: 1px solid #FFFFFF;\n"
"    border-radius: 5px;\n"
"    margin-top: 6px;\n"
"}\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    subcontrol-position: top center;\n"
"    padding: 0 3px;\n"
"    color: #FFFFFF;\n"
"}\n"
"\n"
"/* Таблицы */\n"
"QTableView {\n"
"    background-color: #FFFFFF;\n"
"    color: #000000;\n"
"    border: none;\n"
"    gridline-color: #000000;\n"
"    selection-background-color: #AAAAAA;\n"
"}\n"
"\n"
"/* Списки */\n"
"QListWidget, QTreeWidget {\n"
"    background-color: #FFFFFF;\n"
"    color: #000000;\n"
"    border: none;\n"
"}")
        self.Title = QtWidgets.QLabel(Form)
        self.Title.setGeometry(QtCore.QRect(0, 0, 301, 91))
        self.Title.setTextFormat(QtCore.Qt.PlainText)
        self.Title.setAlignment(QtCore.Qt.AlignCenter)
        self.Title.setWordWrap(False)
        self.Title.setObjectName("Title")
        self.Btc_Adress = QtWidgets.QLabel(Form)
        self.Btc_Adress.setGeometry(QtCore.QRect(40, 190, 221, 20))
        self.Btc_Adress.setAlignment(QtCore.Qt.AlignCenter)
        self.Btc_Adress.setObjectName("Btc_Adress")
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(40, 250, 231, 51))
        self.lineEdit.setObjectName("lineEdit")
        self.Transaction = QtWidgets.QPushButton(Form)
        self.Transaction.setGeometry(QtCore.QRect(80, 380, 140, 41))
        self.Transaction.setObjectName("Transaction")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.Title.setText(_translate("Form", "Wallet"))
        self.Btc_Adress.setText(_translate("Form", "Введиите адрес кошелька"))
        self.Transaction.setText(_translate("Form", "Отправить"))
