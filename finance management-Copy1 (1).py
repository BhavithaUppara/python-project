#!/usr/bin/env python
# coding: utf-8

# In[1]:


import bcrypt
import sqlite3

# Database initialization
conn = sqlite3.connect('finance.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')

def register_user():
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        print("Registration successful!")
    except sqlite3.IntegrityError:
        print("Username already exists. Please choose another.")

register_user()


# In[2]:


cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY, user_id INTEGER, type TEXT, amount REAL, 
    category TEXT, date TEXT, FOREIGN KEY(user_id) REFERENCES users(id))''')

def add_transaction(user_id, transaction_type):
    amount = float(input(f"Enter {transaction_type} amount: "))
    category = input("Enter category: ")
    date = input("Enter date (YYYY-MM-DD): ")
    cursor.execute('''INSERT INTO transactions (user_id, type, amount, category, date) 
                      VALUES (?, ?, ?, ?, ?)''', 
                   (user_id, transaction_type, amount, category, date))
    conn.commit()
    print(f"{transaction_type.capitalize()} added successfully!")

add_transaction(1, 'income')  # Example call


# In[3]:


from tabulate import tabulate

def generate_monthly_report(user_id, month):
    cursor.execute('''SELECT type, category, SUM(amount) 
                      FROM transactions WHERE user_id = ? AND strftime('%m', date) = ? 
                      GROUP BY type, category''', (user_id, month))
    report = cursor.fetchall()
    print(tabulate(report, headers=["Type", "Category", "Total"], tablefmt="pretty"))

generate_monthly_report(1, '10')  # Example for October


# In[6]:


cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
    user_id INTEGER, category TEXT, budget REAL, 
    FOREIGN KEY(user_id) REFERENCES users(id))''')

def set_budget(user_id, category, amount):
    cursor.execute("INSERT INTO budgets (user_id, category, budget) VALUES (?, ?, ?)", 
                   (user_id, category, amount))
    conn.commit()
    print(f"Budget for {category} set to {amount}")

def check_budget(user_id):
    cursor.execute('''SELECT b.category, b.budget, IFNULL(SUM(t.amount), 0) 
                      FROM budgets b LEFT JOIN transactions t 
                      ON b.user_id = t.user_id AND b.category = t.category 
                      WHERE b.user_id = ? GROUP BY b.category''', (user_id,))
    for category, budget, spent in cursor.fetchall():
        if spent > budget:
            print(f"Warning: You have exceeded the budget for {category}!")
        else:
            print(f"{category}: {spent}/{budget} within budget.")

check_budget(1)  # Example check


# In[7]:


import shutil

def backup_database():
    shutil.copy('finance.db', 'finance_backup.db')
    print("Backup successful!")

def restore_database():
    shutil.copy('finance_backup.db', 'finance.db')
    print("Database restored!")

backup_database()  # Example backup


# In[10]:


import unittest

class TestFinanceApp(unittest.TestCase):
    def test_add_transaction(self):
        # Mock adding a transaction and validate the result
        result = add_transaction(1, 'income')  # Example mock
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()


# In[ ]:




