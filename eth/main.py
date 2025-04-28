import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from web3 import Web3
from bitcoinlib.wallets import Wallet

# Настройка подключения к Ethereum Testnet (Goerli)
ETH_NODE = "https://mainnet.infura.io/v3/ff800702763545ea89564b783c0453a5"  # Замените на свой Infura API для тестнета
web3 = Web3(Web3.HTTPProvider(ETH_NODE))

# Файл для хранения данных кошельков
WALLET_FILE = "wallets.json"

# Если файла не существует, создаём пустой JSON
if not os.path.exists(WALLET_FILE):
    with open(WALLET_FILE, "w") as file:
        json.dump({}, file)


def load_wallets():
    with open(WALLET_FILE, "r") as file:
        return json.load(file)


def save_wallets(data):
    with open(WALLET_FILE, "w") as file:
        json.dump(data, file, indent=4)


def create_wallet():
    username = simpledialog.askstring("Создание кошелька", "Введите имя пользователя:")
    if not username:
        return

    wallets = load_wallets()

    if username in wallets:
        messagebox.showerror("Ошибка", "Такой пользователь уже существует!")
        return

    # Генерация ETH-кошелька (тестнет)
    eth_account = web3.eth.account.create()
    eth_address = eth_account.address
    eth_private_key = eth_account.key.hex()

    # Генерация BTC-кошелька (testnet)
    # Передаём параметр network='testnet'
    btc_wallet = Wallet.create(username, network='testnet')
    key = btc_wallet.get_key()
    btc_address = key.address
    btc_private_key = key.wif

    wallets[username] = {
        "ETH": {"address": eth_address, "private_key": eth_private_key},
        "BTC": {"address": btc_address, "private_key": btc_private_key},
    }

    save_wallets(wallets)

    messagebox.showinfo("Успех", f"Кошелек {username} создан!\n\nETH: {eth_address}\nBTC: {btc_address}")


def check_balance():
    username = simpledialog.askstring("Проверка баланса", "Введите имя пользователя:")
    if not username:
        return

    wallets = load_wallets()
    if username not in wallets:
        messagebox.showerror("Ошибка", "Кошелек не найден!")
        return

    eth_address = wallets[username]["ETH"]["address"]

    # Проверка ETH баланса (на тестнете)
    eth_balance = web3.eth.get_balance(eth_address)
    eth_balance = web3.from_wei(eth_balance, "ether")

    # Проверка BTC баланса (используем bitcoinlib для testnet)
    btc_wallet = Wallet(username, network='testnet')
    btc_balance = btc_wallet.balance()

    messagebox.showinfo(
        "Баланс",
        f"ETH: {eth_balance} ETH\nBTC: {btc_balance} BTC",
    )


def send_eth():
    username = simpledialog.askstring("Отправка ETH", "Введите имя отправителя:")
    recipient = simpledialog.askstring("Отправка ETH", "Введите адрес получателя:")
    amount = simpledialog.askfloat("Отправка ETH", "Введите сумму в ETH:")

    if not username or not recipient or amount is None:
        return

    wallets = load_wallets()
    if username not in wallets:
        messagebox.showerror("Ошибка", "Кошелек не найден!")
        return

    sender_private_key = wallets[username]["ETH"]["private_key"]
    sender_address = wallets[username]["ETH"]["address"]

    nonce = web3.eth.get_transaction_count(sender_address)
    gas_price = web3.eth.gas_price

    tx = {
        "nonce": nonce,
        "to": recipient,
        "value": web3.to_wei(amount, "ether"),
        "gas": 21000,
        "gasPrice": gas_price,
    }

    signed_tx = web3.eth.account.sign_transaction(tx, sender_private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    messagebox.showinfo("Успех", f"Транзакция отправлена!\nTx Hash: {tx_hash.hex()}")


def send_btc():
    username = simpledialog.askstring("Отправка BTC", "Введите имя отправителя:")
    recipient = simpledialog.askstring("Отправка BTC", "Введите адрес получателя:")
    amount = simpledialog.askfloat("Отправка BTC", "Введите сумму в BTC:")

    if not username or not recipient or amount is None:
        return
        
    wallets = load_wallets()
    if username not in wallets:
        messagebox.showerror("Ошибка", "Кошелек не найден!")
        return

    # Получаем BTC-кошелек для testnet
    btc_wallet = Wallet(username, network='testnet')
    try:
        tx = btc_wallet.send_to(recipient, amount)
        messagebox.showinfo("Успех", f"Транзакция отправлена!\nTx ID: {tx.txid}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка отправки BTC: {str(e)}")


# Создание UI с помощью tkinter
root = tk.Tk()
root.title("Криптокошелек BTC/ETH (Testnet)")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

tk.Button(frame, text="Создать кошелек", command=create_wallet, width=25).pack(pady=5)
tk.Button(frame, text="Проверить баланс", command=check_balance, width=25).pack(pady=5)
tk.Button(frame, text="Отправить ETH", command=send_eth, width=25).pack(pady=5)
tk.Button(frame, text="Отправить BTC", command=send_btc, width=25).pack(pady=5)
tk.Button(frame, text="Выход", command=root.quit, width=25).pack(pady=5)

root.mainloop()