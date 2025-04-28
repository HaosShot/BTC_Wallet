import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from bitcoinlib.wallets import Wallet
from bitcoinlib.mnemonic import Mnemonic
from bitcoinlib.keys import HDKey
import webbrowser
import logging
from bitcoinlib.services.services import Service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WALLET_FILE = "bitcoin_wallets.json"

class BitcoinTestnetWallet:
    def __init__(self):
        self.wallets = self.load_wallets()
        self.setup_gui()
        
    def load_wallets(self):
        if not os.path.exists(WALLET_FILE):
            with open(WALLET_FILE, 'w') as f:
                json.dump({}, f)
            return {}
        with open(WALLET_FILE) as f:
            return json.load(f)
    
    def save_wallets(self):
        with open(WALLET_FILE, 'w') as f:
            json.dump(self.wallets, f, indent=4)
    
    def create_wallet(self):
        wallet_name = simpledialog.askstring("Создание кошелька", "Введите имя кошелька:")
        if not wallet_name:
            return
            
        if wallet_name in self.wallets:
            messagebox.showerror("Ошибка", "Кошелек с таким именем уже существует!")
            return
            
        mnemonic = Mnemonic().generate()
        hdkey = HDKey.from_passphrase(mnemonic, network='testnet')
        key = hdkey.subkey_for_path("m/84'/1'/0'/0/0")
        
        self.wallets[wallet_name] = {
            'mnemonic': mnemonic,
            'address': key.address(),
            'private_key': key.wif(),
            'network': 'testnet'
        }
        self.save_wallets()
        
        messagebox.showinfo(
            "Успех", 
            f"Кошелек {wallet_name} создан!\n\n"
            f"Адрес: {key.address()}\n"
            f"Приватный ключ (WIF): {key.wif()}\n"
            f"Мнемоническая фраза (запишите!):\n{mnemonic}"
        )
    
    def get_faucet(self):
        wallet_name = simpledialog.askstring("Получить тестовые BTC", "Введите имя кошелька:")
        if not wallet_name or wallet_name not in self.wallets:
            messagebox.showerror("Ошибка", "Кошелек не найден!")
            return
            
        address = self.wallets[wallet_name]['address']
        webbrowser.open(f"https://coinfaucet.eu/en/btc-testnet/?address={address}")
        messagebox.showinfo("Успех", f"Перейдите на сайт фаусета и введите адрес:\n{address}")
    
    def send_transaction(self):
        wallet_name = simpledialog.askstring("Отправить BTC", "Введите имя вашего кошелька:")
        if not wallet_name or wallet_name not in self.wallets:
            messagebox.showerror("Ошибка", "Кошелек не найден!")
            return

        recipient = simpledialog.askstring("Отправить BTC", "Введите адрес получателя:")
        if not recipient or not (recipient.startswith('tb1') or recipient.startswith('2') or recipient.startswith('m') or recipient.startswith('n')):
            messagebox.showerror("Ошибка", "Неверный формат адреса!")
            return

        try:
            amount_str = simpledialog.askstring("Отправить BTC", "Введите сумму в BTC:")
            amount = float(amount_str)  
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть больше 0")
                return
        except (ValueError, TypeError):
            messagebox.showerror("Ошибка", "Неверный формат суммы. Введите число, например: 0.01")
            return

        try:
            service = Service(network='testnet')
            wallet_data = self.wallets[wallet_name]
            address = wallet_data['address']
            private_key_wif = wallet_data['private_key']

            utxos = service.getutxos(address)
            if not utxos:
                messagebox.showerror("Ошибка", "Нет средств для отправки! Пополните кошелек через faucet.")
                return

            from bitcoinlib.transactions import Transaction
            from bitcoinlib.keys import Key

            t = Transaction(network='testnet')
            total_input = 0

            fee_per_byte = service.estimatefee()
            if fee_per_byte is None or fee_per_byte <= 0:
                fee_per_byte = 10
            estimated_fee = int(fee_per_byte * 250)

            required_amount = int(amount * 100000000) + estimated_fee

            selected_utxos = []
            for utxo in utxos:
                selected_utxos.append(utxo)
                total_input += utxo['value']
                if total_input >= required_amount:
                    break

            if total_input < required_amount:
                messagebox.showerror("Ошибка", 
                    f"Недостаточно средств!\n"
                    f"Нужно: {amount + estimated_fee / 100000000:.6f} BTC\n"
                    f"Доступно: {total_input / 100000000:.6f} BTC")
                return

            for utxo in selected_utxos:
                t.add_input(utxo['txid'], utxo['output_n'])

            t.add_output(recipient, int(amount * 100000000))

            change = total_input - required_amount
            if change > 0:
                t.add_output(address, change)

            key = Key(private_key_wif, network='testnet')
            t.sign(key)

            tx_id = service.sendrawtransaction(t.raw_hex())

            tx_url = f"https://blockstream.info/testnet/tx/{tx_id}"
            messagebox.showinfo(
                "Успех", 
                f"Транзакция отправлена!\n\n"
                f"ID: {tx_id}\n"
                f"Адрес: {recipient}\n"
                f"Сумма: {amount:.6f} BTC\n"
                f"Комиссия: {estimated_fee / 100000000:.6f} BTC\n"
                f"Просмотр: {tx_url}"
            )
            webbrowser.open(tx_url)

        except Exception as e:
            logger.error(f"Ошибка отправки: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось отправить транзакцию:\n{str(e)}")

    
    def check_balance(self):
        wallet_name = simpledialog.askstring("Проверить баланс", "Введите имя кошелька:")
        if not wallet_name or wallet_name not in self.wallets:
            messagebox.showerror("Ошибка", "Кошелек не найден!")
            return
            
        try:
            service = Service(network='testnet')
            address = self.wallets[wallet_name]['address']
            balance = service.getbalance(address)
            
            messagebox.showinfo(
                "Баланс",
                f"Кошелек: {wallet_name}\n"
                f"Адрес: {address}\n"
                f"Баланс: {balance / 100000000} BTC"
            )
            
        except Exception as e:
            logger.error(f"Ошибка проверки баланса: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось проверить баланс:\n{str(e)}")


    
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Bitcoin Testnet Wallet")
        
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack()
        
        tk.Button(frame, text="Создать кошелек", command=self.create_wallet, width=25).pack(pady=5)
        tk.Button(frame, text="Получить тестовые BTC", command=self.get_faucet, width=25).pack(pady=5)
        tk.Button(frame, text="Отправить BTC", command=self.send_transaction, width=25).pack(pady=5)
        tk.Button(frame, text="Проверить баланс", command=self.check_balance, width=25).pack(pady=5)
        tk.Button(frame, text="Выход", command=self.root.quit, width=25).pack(pady=5)
        
        self.root.mainloop()

if __name__ == "__main__":
    BitcoinTestnetWallet()