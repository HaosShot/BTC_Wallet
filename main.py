import sys
import sqlite3
import os
import requests
import webbrowser
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from bitcoinlib.wallets import Wallet, wallet_delete
from bitcoinlib.mnemonic import Mnemonic
from bitcoinlib.transactions import Transaction
from bitcoinlib.services.services import Service
from decimal import Decimal, InvalidOperation

DB_FILE = os.path.join(os.path.dirname(__file__), 'btc.db')
NETWORK = 'testnet'
MEMPOOL_URL = 'https://mempool.space/testnet'
FAUCET_URL = 'https://bitcoinfaucet.uo1.net/'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                btc_address TEXT,
                wallet_name TEXT UNIQUE,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()

init_db()

class BalanceWorker(QThread):
    balance_updated = pyqtSignal(float, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, btc_address):
        super().__init__()
        self.btc_address = btc_address

    def run(self):
        try:
            response = requests.get(
                f"{MEMPOOL_URL}/api/address/{self.btc_address}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                confirmed = data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']
                unconfirmed = data['mempool_stats']['funded_txo_sum'] - data['mempool_stats']['spent_txo_sum']
                total_balance = (confirmed + unconfirmed) / 100_000_000
                self.balance_updated.emit(total_balance, self.btc_address)
            else:
                self.error_occurred.emit(f"Ошибка API: {response.status_code}")
        except Exception as e:
            self.error_occurred.emit(f"Ошибка соединения: {str(e)}")

class AuthWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bitcoin Testnet Wallet")
        self.setFixedSize(400, 300)
        
        self.title_label = QtWidgets.QLabel("Bitcoin Testnet Wallet", self)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.title_label.setGeometry(0, 20, 400, 30)
        
        self.register_btn = QtWidgets.QPushButton("Регистрация", self)
        self.register_btn.setGeometry(100, 100, 200, 40)
        
        self.signin_btn = QtWidgets.QPushButton("Вход", self)
        self.signin_btn.setGeometry(100, 160, 200, 40)
        
        self.register_btn.clicked.connect(self.open_register)
        self.signin_btn.clicked.connect(self.open_signin)
        
    def open_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.hide()
        
    def open_signin(self):
        self.signin_window = SignInWindow()
        self.signin_window.show()
        self.hide()

class RegisterWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.setFixedSize(400, 300)
        
        self.title_label = QtWidgets.QLabel("Регистрация", self)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.title_label.setGeometry(0, 20, 400, 30)
        
        self.username_label = QtWidgets.QLabel("Имя пользователя:", self)
        self.username_label.setGeometry(50, 70, 300, 20)
        
        self.username_input = QtWidgets.QLineEdit(self)
        self.username_input.setGeometry(50, 95, 300, 30)
        
        self.password_label = QtWidgets.QLabel("Пароль:", self)
        self.password_label.setGeometry(50, 135, 300, 20)
        
        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setGeometry(50, 160, 300, 30)
        
        self.register_btn = QtWidgets.QPushButton("Зарегистрироваться", self)
        self.register_btn.setGeometry(100, 210, 200, 40)
        
        self.back_btn = QtWidgets.QPushButton("Назад", self)
        self.back_btn.setGeometry(100, 260, 200, 30)
        
        self.register_btn.clicked.connect(self.register_user)
        self.back_btn.clicked.connect(self.back_to_auth)
        
    def register_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Все поля должны быть заполнены!')
            return

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                if cursor.fetchone():
                    QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Пользователь уже существует!')
                    return

                wallet_name = f"wallet_{username}"
                mnemonic = Mnemonic().generate()
                
                wallet = Wallet.create(
                    name=wallet_name,
                    keys=mnemonic,
                    network=NETWORK
                )
                
                address = wallet.get_key().address

                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                user_id = cursor.lastrowid
                cursor.execute('''
                    INSERT INTO wallets (user_id, btc_address, wallet_name)
                    VALUES (?, ?, ?)
                ''', (user_id, address, wallet_name))
                conn.commit()

                QtWidgets.QMessageBox.information(
                    self,
                    'Регистрация успешна',
                    f"Ваш кошелек создан!\n\n"
                    f"Адрес: {address}\n\n"
                    f"Мнемоническая фраза (сохраните!):\n{mnemonic}"
                )
                
                self.main_window = MainWindow(user_id, username, address, wallet_name)
                self.main_window.show()
                self.hide()

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Ошибка', f'Ошибка регистрации:\n{str(e)}')
                if 'wallet' in locals():
                    wallet_delete(wallet_name, force=True)
                    
    def back_to_auth(self):
        self.auth_window = AuthWindow()
        self.auth_window.show()
        self.hide()

class SignInWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход")
        self.setFixedSize(400, 300)
        
        self.title_label = QtWidgets.QLabel("Вход", self)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.title_label.setGeometry(0, 20, 400, 30)
        
        self.username_label = QtWidgets.QLabel("Имя пользователя:", self)
        self.username_label.setGeometry(50, 70, 300, 20)
        
        self.username_input = QtWidgets.QLineEdit(self)
        self.username_input.setGeometry(50, 95, 300, 30)
        
        self.password_label = QtWidgets.QLabel("Пароль:", self)
        self.password_label.setGeometry(50, 135, 300, 20)
        
        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setGeometry(50, 160, 300, 30)
        
        self.signin_btn = QtWidgets.QPushButton("Войти", self)
        self.signin_btn.setGeometry(100, 210, 200, 40)
        
        self.back_btn = QtWidgets.QPushButton("Назад", self)
        self.back_btn.setGeometry(100, 260, 200, 30)
        
        self.signin_btn.clicked.connect(self.sign_in_user)
        self.back_btn.clicked.connect(self.back_to_auth)
        
    def sign_in_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Все поля должны быть заполнены!')
            return

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    SELECT users.id, wallets.btc_address, wallets.wallet_name
                    FROM users
                    JOIN wallets ON users.id = wallets.user_id
                    WHERE username = ? AND password = ?
                ''', (username, password))

                result = cursor.fetchone()
                if result:
                    user_id, address, wallet_name = result
                    self.main_window = MainWindow(user_id, username, address, wallet_name)
                    self.main_window.show()
                    self.hide()
                else:
                    QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Неверные данные!')
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Ошибка', f'Ошибка входа:\n{str(e)}')
                
    def back_to_auth(self):
        self.auth_window = AuthWindow()
        self.auth_window.show()
        self.hide()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, user_id, username, btc_address, wallet_name):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.btc_address = btc_address
        self.wallet_name = wallet_name
        
        self.setWindowTitle(f"Bitcoin Wallet - {username}")
        self.setFixedSize(600, 400)
        
        self.title_label = QtWidgets.QLabel(f"Кошелек {username}", self)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.title_label.setGeometry(0, 20, 600, 30)
        
        self.address_label = QtWidgets.QLabel(f"Адрес: {btc_address}", self)
        self.address_label.setGeometry(50, 70, 500, 20)
        
        self.balance_label = QtWidgets.QLabel("Баланс: загрузка...", self)
        self.balance_label.setGeometry(50, 100, 500, 20)
        
        self.receive_btn = QtWidgets.QPushButton("Получить BTC", self)
        self.receive_btn.setGeometry(50, 150, 200, 40)
        
        self.send_btn = QtWidgets.QPushButton("Отправить BTC", self)
        self.send_btn.setGeometry(350, 150, 200, 40)
        
        self.new_address_btn = QtWidgets.QPushButton("Новый адрес", self)
        self.new_address_btn.setGeometry(200, 210, 200, 40)
        
        self.receive_btn.clicked.connect(self.show_receive)
        self.send_btn.clicked.connect(self.show_send)
        self.new_address_btn.clicked.connect(self.generate_new_address)
        
        self.update_balance()
        self.balance_timer = QtCore.QTimer(self)
        self.balance_timer.timeout.connect(self.update_balance)
        self.balance_timer.start(30000)
        
    def update_balance(self):
        self.balance_worker = BalanceWorker(self.btc_address)
        self.balance_worker.balance_updated.connect(self.on_balance_updated)
        self.balance_worker.error_occurred.connect(self.on_balance_error)
        self.balance_worker.start()
        
    def on_balance_updated(self, balance, address):
        if address == self.btc_address:
            self.balance_label.setText(f"Баланс: {balance:.8f} BTC")
            
    def on_balance_error(self, error_msg):
        self.balance_label.setText("Баланс: ошибка обновления")
        print(error_msg)
        
    def generate_new_address(self):
        try:
            wallet = Wallet(self.wallet_name)
            new_address = wallet.get_key().address
            self.btc_address = new_address
            self.address_label.setText(f"Адрес: {new_address}")
            
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE wallets SET btc_address = ? WHERE wallet_name = ?
                ''', (new_address, self.wallet_name))
                conn.commit()
                
            QtWidgets.QMessageBox.information(
                self, 
                "Новый адрес", 
                f"Сгенерирован новый адрес:\n{new_address}"
            )
            self.update_balance()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                'Ошибка',
                f"Не удалось сгенерировать адрес:\n{str(e)}"
            )
            
    def show_receive(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Получить BTC")
        msg.setText(f"Ваш адрес:\n\n{self.btc_address}")
        
        open_faucet = msg.addButton("Фаусет", QtWidgets.QMessageBox.AcceptRole)
        copy_btn = msg.addButton("Копировать", QtWidgets.QMessageBox.ActionRole)
        msg.addButton(QtWidgets.QMessageBox.Close)
        
        msg.exec_()
        
        if msg.clickedButton() == open_faucet:
            webbrowser.open(FAUCET_URL)
        elif msg.clickedButton() == copy_btn:
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(self.btc_address)
            QtWidgets.QMessageBox.information(self, "Скопировано", "Адрес в буфере обмена")
            
    def show_send(self):
        self.transaction_window = TransactionWindow(
            self.username, 
            self.btc_address, 
            self.wallet_name
        )
        self.transaction_window.show()

class TransactionWindow(QtWidgets.QWidget):
    def __init__(self, username, btc_address, wallet_name):
        super().__init__()
        self.username = username
        self.sender_address = btc_address
        self.wallet_name = wallet_name
        self.current_balance_sat = 0
        self.MIN_FEE_RATE = 5  
        
        self.setWindowTitle("Отправить BTC")
        self.setFixedSize(500, 500)
    
        self.amount_validator = QtGui.QRegExpValidator(
            QtCore.QRegExp(r"^[0-9]+([\.,][0-9]{1,8})?$"), self)
        self.fee_validator = QtGui.QIntValidator(self.MIN_FEE_RATE, 500, self)
    
        self.address_input = QtWidgets.QLineEdit()
        self.amount_input = QtWidgets.QLineEdit()
        self.fee_input = QtWidgets.QLineEdit(str(self.MIN_FEE_RATE))
        
        self.init_ui()
        self.update_balance()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        
        title = QtWidgets.QLabel("Отправить Bitcoin")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        layout.addWidget(QtWidgets.QLabel("Адрес получателя (Testnet3):"))
        self.address_input.setPlaceholderText("tb1q... или m/n/2...")
        layout.addWidget(self.address_input)
        
        layout.addWidget(QtWidgets.QLabel("Сумма (BTC):"))
        self.amount_input.setPlaceholderText("0.0001 или 0,0001")
        self.amount_input.setValidator(self.amount_validator)
        layout.addWidget(self.amount_input)
        
        layout.addWidget(QtWidgets.QLabel(f"Комиссия (sat/byte, минимум {self.MIN_FEE_RATE}):"))
        self.fee_input.setValidator(self.fee_validator)
        layout.addWidget(self.fee_input)
      
        self.balance_label = QtWidgets.QLabel()
        self.balance_label.setStyleSheet("font-size: 13px; color: #555;")
        layout.addWidget(self.balance_label)
   
        btn_layout = QtWidgets.QHBoxLayout()
        self.send_btn = QtWidgets.QPushButton("Отправить")
        self.send_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.send_btn.clicked.connect(self.send_transaction)
        
        self.back_btn = QtWidgets.QPushButton("Назад")
        self.back_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.send_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

    def update_balance(self):
        try:
            response = requests.get(f"{MEMPOOL_URL}/api/address/{self.sender_address}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                confirmed = data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']
                unconfirmed = data['mempool_stats']['funded_txo_sum'] - data['mempool_stats']['spent_txo_sum']
                self.current_balance_sat = confirmed + unconfirmed
                balance_btc = self.current_balance_sat / 100_000_000
                self.balance_label.setText(
                    f"Доступно: {balance_btc:.8f} BTC ({self.current_balance_sat} сатоши)\n"
                    f"Подтверждено: {confirmed/100_000_000:.8f} BTC\n"
                    f"Не подтверждено: {unconfirmed/100_000_000:.8f} BTC"
                )
        except Exception as e:
            self.balance_label.setText("Ошибка загрузки баланса")
            print(f"Ошибка обновления баланса: {e}")

    def send_transaction(self):
        try:
            # Валидация 
            recipient = self.address_input.text().strip()
            if not recipient or not self.is_valid_testnet_address(recipient):
                self.show_error("Некорректный Testnet3 адрес")
                return
            try:
                amount_input = self.amount_input.text().strip().replace(',', '.')
                amount_sat = int(Decimal(amount_input) * 100_000_000)
                if amount_sat <= 0:
                    raise ValueError
            except (InvalidOperation, ValueError):
                self.show_error("Некорректная сумма (пример: 0.0001)")
                return
            
            # Валидация 
            try:
                fee_rate = int(self.fee_input.text().strip())
                if fee_rate < self.MIN_FEE_RATE or fee_rate > 500:
                    raise ValueError
            except:
                self.show_error(f"Комиссия должна быть от {self.MIN_FEE_RATE} до 500 sat/byte")
                return
            
            # Расчет комиссии
            estimated_tx_size = 200  
            total_fee = fee_rate * estimated_tx_size
            total_spend = amount_sat + total_fee
            
            # Проверка баланса
            if total_spend > self.current_balance_sat:
                self.show_error(
                    f"Недостаточно средств!\n"
                    f"Требуется: {total_spend} сатоши\n"
                    f"Доступно: {self.current_balance_sat} сатоши"
                )
                return
            
            # Подтверждение
            confirm_msg = (
                f"Подтвердите отправку:\n\n"
                f"▪ Сумма: {amount_sat} сатоши ({amount_sat/100_000_000:.8f} BTC)\n"
                f"▪ Адрес: {recipient[:12]}...{recipient[-4:]}\n"
                f"▪ Комиссия: {fee_rate} sat/byte\n"
                f"▪ Общая комиссия: {total_fee} сатоши\n\n"
                f"Всего к списанию: {total_spend} сатоши"
            )
            
            if QtWidgets.QMessageBox.question(
                self, "Подтверждение", confirm_msg,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            ) != QtWidgets.QMessageBox.Yes:
                return
            
            # Создание транзакции
            wallet = Wallet(self.wallet_name)
            wallet.scan()  
            
            if not wallet.utxos():
                raise Exception("Нет доступных UTXO")
            
            tx = wallet.send_to(
                recipient,
                amount_sat,
                fee=total_fee,
                network=NETWORK,
                broadcast=True
            )
            
            if not tx:
                raise Exception("Ошибка создания транзакции")
            
            self.show_success(tx.txid, amount_sat, fee_rate, total_fee)
            self.update_balance()
                
        except Exception as e:
            self.handle_send_error(e)

    def show_error(self, message):
        QtWidgets.QMessageBox.critical(self, "Ошибка", message)
    
    def show_success(self, txid, amount_sat, fee_rate, total_fee):
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Успешно")
        msg.setText(
            f"Транзакция отправлена!\n\n"
            f"▪ TXID: {txid}\n"
            f"▪ Сумма: {amount_sat} сатоши\n"
            f"▪ Комиссия: {total_fee} сатоши ({fee_rate} sat/byte)"
        )
        
        view_btn = msg.addButton("Открыть в Mempool", QtWidgets.QMessageBox.AcceptRole)
        msg.addButton("Закрыть", QtWidgets.QMessageBox.RejectRole)
        msg.exec_()
        
        if msg.clickedButton() == view_btn:
            webbrowser.open(f"{MEMPOOL_URL}/tx/{txid}")

    def handle_send_error(self, error):
        error_msg = str(error)
        if "insufficient" in error_msg.lower():
            error_msg = "Недостаточно средств для покрытия комиссии"
        elif "utxo" in error_msg.lower():
            error_msg = "Нет непотраченных выходов (UTXO)"
        elif "fee" in error_msg.lower():
            error_msg = "Слишком низкая комиссия"
        
        QtWidgets.QMessageBox.critical(
            self, 
            "Ошибка отправки", 
            f"{error_msg}\n\nПроверьте:\n1. Баланс\n2. Комиссию\n3. Подключение к сети"
        )

    def is_valid_testnet_address(self, address):
        testnet_prefixes = ('m', 'n', '2', 'tb1')
        return address.lower().startswith(testnet_prefixes)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    app.setStyle('Fusion')
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(142, 45, 197).lighter())
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(palette)
    
    auth_window = AuthWindow()
    auth_window.show()
    
    sys.exit(app.exec_())