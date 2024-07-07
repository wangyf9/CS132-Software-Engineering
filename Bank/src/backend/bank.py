import sqlite3

def initialize_database():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        balance REAL NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id TEXT NOT NULL,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        starting_balance REAL NOT NULL,
        ending_balance REAL NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

def reset_database():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS accounts')
    cursor.execute('DROP TABLE IF EXISTS transactions')
    conn.commit()
    conn.close()
    initialize_database()  # Recreate tables