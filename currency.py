import json
import os

DATA_FILE = "balances.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        balances = json.load(f)
else:
    balances = {}

def get_balance(user_id: int):
    return balances.get(str(user_id), 100)

def add_balance(user_id: int, amount: int):
    user_id = str(user_id)
    balances[user_id] = get_balance(user_id) + amount
    save()

def remove_balance(user_id: int, amount: int):
    user_id = str(user_id)
    balances[user_id] = get_balance(user_id) - amount
    save()

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(balances, f)
