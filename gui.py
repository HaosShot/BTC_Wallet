import json
import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QLineEdit, QHBoxLayout, QRadioButton, QGroupBox, QMessageBox
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from web3 import Web3
from eth_account import Account
import secrets
import webbrowser

INFURA_URL = "https://sepolia.infura.io/v3/3b8e2d8a60f7442984eb60ff7ca9e458"  

class WalletApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Wallet App")
        self.setGeometry(200, 200, 400, 600)

        self.setStyleSheet("background-color: #001f3d; color: white;")

        self.stack = QStackedWidget(self)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.stack)

        self.current_wallet = None
        self.wallet_address = None

        self.init_login_screen()
        self.init_main_screen()
        self.init_send_selection_screen()
        self.init_send_screen()
        self.init_receive_screen()

        # Устанавливаем начальный экран
        self.stack.setCurrentIndex(0)

    def init_login_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)

        title = QLabel("Войти или создать кошелек")
        title.setFont(QFont("Arial", 14))
        title.setAlignment(Qt.AlignCenter)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя кошелька")
        self.name_input.setStyleSheet("background-color: white; color: black;")

        create_btn = QPushButton("Создать новый")
        create_btn.setStyleSheet("background-color: lightgray; color: black;")  
        create_btn.clicked.connect(self.create_wallet)

        login_btn = QPushButton("Войти")
        login_btn.setStyleSheet("background-color: lightgray; color: black;")  
        login_btn.clicked.connect(self.login_wallet)

        layout.addWidget(title)
        layout.addWidget(self.name_input)
        layout.addWidget(create_btn)
        layout.addWidget(login_btn)

        self.stack.addWidget(screen)

    def create_wallet(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите имя")
            return

        acct = Account.create(secrets.token_hex(32))
        data = {
            "eth_address": acct.address,
            "eth_private": acct.key.hex(),
            "btc_address": secrets.token_hex(16)[:16],
            "btc_balance": 0
        }
        wallets = self.load_wallets()
        wallets[name] = data
        self.save_wallets(wallets)

        QMessageBox.information(self, "Кошелек создан", f"Кошелек {name} создан!\n\nАдрес: {acct.address}\nПриватный ключ: {acct.key.hex()}")

    def login_wallet(self):
        name = self.name_input.text().strip()
        wallets = self.load_wallets()

        if name in wallets:
            self.current_wallet = wallets[name]
            self.wallet_address = self.current_wallet['eth_address']

            print(f"Успешный вход. Адрес: {self.wallet_address}")  
            
            self.update_balances()
            self.stack.setCurrentIndex(1)

            self.init_receive_screen()
        else:
            QMessageBox.warning(self, "Ошибка", "Кошелек не найден")

    def load_wallets(self):
        if os.path.exists("wallets.json"):
            with open("wallets.json", "r") as f:
                return json.load(f)
        return {}

    def save_wallets(self, data):
        with open("wallets.json", "w") as f:
            json.dump(data, f, indent=4)

    def update_balances(self):
        w3 = Web3(Web3.HTTPProvider(INFURA_URL))
        try:
            eth_balance = w3.eth.get_balance(self.wallet_address)
            eth_in_eth = w3.fromWei(eth_balance, 'ether')
        except:
            eth_in_eth = 0

        self.eth_balance_label.setText(f"ETH: {eth_in_eth:.4f}")
        self.btc_balance_label.setText(f"BTC: {self.current_wallet.get('btc_balance', 0)} (test)")

    def init_main_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)

        title = QLabel("Wallet")
        title.setFont(QFont("Arial", 20))
        title.setAlignment(Qt.AlignCenter)
        title.setContentsMargins(0, 20, 0, 10)

        balance_container = QVBoxLayout()
        balance_container.setAlignment(Qt.AlignCenter)

        balance_layout1 = QHBoxLayout()
        eth_icon = QLabel()
        eth_icon.setPixmap(QPixmap("eth.png").scaled(50, 50, Qt.KeepAspectRatio))
        self.eth_balance_label = QLabel("ETH: 0.0000")
        self.eth_balance_label.setStyleSheet("color: white;")
        balance_layout1.addWidget(eth_icon)
        balance_layout1.addWidget(self.eth_balance_label)

        balance_layout2 = QHBoxLayout()
        btc_icon = QLabel()
        btc_icon.setPixmap(QPixmap("btc.png").scaled(50, 50, Qt.KeepAspectRatio))
        self.btc_balance_label = QLabel("BTC: 0 (test)")
        self.btc_balance_label.setStyleSheet("color: white;")
        balance_layout2.addWidget(btc_icon)
        balance_layout2.addWidget(self.btc_balance_label)

        balance_container.addLayout(balance_layout1)
        balance_container.addLayout(balance_layout2)

        button_container = QVBoxLayout()
        button_container.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)

        btn_receive = QPushButton("Получить")
        btn_receive.setStyleSheet("background-color: lightgray; color: black;")  
        btn_receive.clicked.connect(lambda: self.stack.setCurrentIndex(4))

        btn_send = QPushButton("Отправить")
        btn_send.setStyleSheet("background-color: lightgray; color: black;")  
        btn_send.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        button_container.addWidget(btn_receive)
        button_container.addWidget(btn_send)

        layout.addWidget(title)
        layout.addLayout(balance_container)
        layout.addLayout(button_container)

        self.stack.addWidget(screen)

    def init_send_selection_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Выберите валюту")
        title.setFont(QFont("Arial", 20))
        title.setAlignment(Qt.AlignCenter)

        eth_button = QRadioButton("Ethereum")
        eth_button.setStyleSheet("color: white;")
        btc_button = QRadioButton("Bitcoin")
        btc_button.setStyleSheet("color: white;")

        btn_back = QPushButton("Вернуться")
        btn_back.setStyleSheet("background-color: lightgray; color: black;")  
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        btn_next = QPushButton("Далее")
        btn_next.setStyleSheet("background-color: lightgray; color: black;")  
        btn_next.clicked.connect(lambda: self.stack.setCurrentIndex(3))

        layout.addWidget(title)
        layout.addWidget(eth_button)
        layout.addWidget(btc_button)
        layout.addWidget(btn_back)
        layout.addWidget(btn_next)

        self.stack.addWidget(screen)

    def init_send_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Отправить на кошелек")
        title.setFont(QFont("Arial", 20))
        title.setAlignment(Qt.AlignCenter)

        input_address = QLineEdit()
        input_address.setPlaceholderText("Введите адрес получателя")
        input_address.setStyleSheet("background-color: lightgray; color: black;")

        input_amount = QLineEdit()
        input_amount.setPlaceholderText("Введите сумму (ETH)")
        input_amount.setStyleSheet("background-color: lightgray; color: black;")

        btn_back = QPushButton("Вернуться")
        btn_back.setStyleSheet("background-color: lightgray; color: black;")  
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(2))  

        btn_send = QPushButton("Отправить")
        btn_send.setStyleSheet("background-color: lightgray; color: black;")  
        btn_send.clicked.connect(lambda: self.send_eth(input_address.text(), input_amount.text()))  

        layout.addWidget(title)
        layout.addWidget(input_address)
        layout.addWidget(input_amount)
        layout.addWidget(btn_back)
        layout.addWidget(btn_send)

        self.stack.addWidget(screen)

    def send_eth(self, to_address, amount_str):
        if not to_address or not amount_str:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверная сумма.")
            return

        if amount <= 0:
            QMessageBox.warning(self, "Ошибка", "Сумма должна быть больше нуля.")
            return

        w3 = Web3(Web3.HTTPProvider(INFURA_URL))
        try:
            eth_balance = w3.eth.get_balance(self.wallet_address)
            if eth_balance < w3.to_wei(amount, 'ether'):
                QMessageBox.warning(self, "Ошибка", "Недостаточно средств на счете.")
                return
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка получения баланса: {e}")
            return

        private_key = self.current_wallet['eth_private']
        from_address = self.wallet_address
        gas_price = w3.eth.gas_price
        gas_limit = 21000  

        transaction = {
            'to': to_address,
            'value': w3.to_wei(amount, 'ether'),
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': w3.eth.get_transaction_count(from_address),
            'chainId': 1  
        }

        try:
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
            txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            txn_hash_hex = txn_hash.hex()

            QMessageBox.information(self, "Успех", f"Транзакция отправлена! Хэш: {txn_hash_hex}")
            self.update_balances()

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при отправке транзакции: {e}")

    def get_test_eth(self):
        if not self.wallet_address:
            QMessageBox.warning(self, "Ошибка", "Сначала войдите в кошелек.")
            return
        webbrowser.open(f"https://goerlifaucet.com/?address={self.wallet_address}")
        QMessageBox.information(self, "Фаусет", "Перейдите по ссылке, чтобы запросить тестовый ETH.")

    def init_receive_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Получить валюту")
        title.setFont(QFont("Arial", 20))
        title.setAlignment(Qt.AlignCenter)

        if self.wallet_address:
            address_label = QLabel(f"Ваш адрес: {self.wallet_address}")
            address_label.setStyleSheet("color: white;")
        else:
            address_label = QLabel("Адрес не найден. Пожалуйста, войдите в кошелек.")
            address_label.setStyleSheet("color: white;")
        
        print(f"Адрес на экране 'Получить валюту': {self.wallet_address}")  

        btn_back = QPushButton("Вернуться")
        btn_back.setStyleSheet("background-color: lightgray; color: black;")  
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        layout.addWidget(title)
        layout.addWidget(address_label)
        layout.addWidget(btn_back)

        self.stack.addWidget(screen)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WalletApp()
    window.show()
    sys.exit(app.exec_())
