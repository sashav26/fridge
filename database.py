import sqlite3
import re

def setup_database():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            cost REAL,
            quantity INTEGER,
            transaction_date TEXT
        )
    ''')
    conn.commit()
    return conn, cursor

import re

def save_to_database(extracted_data, cursor, conn):
    for item in extracted_data.get("line_items", []):
        item_name = item.get("item_name", "Unknown Item")

        # Remove leading numbers from the item name
        item_name = re.sub(r'^\d+\s*', '', item_name)

        item_value = item.get("item_value", "").replace("$", "").strip()

        if not item_value:
            print(f"Skipping item with no price: {item_name}")
            continue

        try:
            cost = float(item_value)
        except ValueError:
            print(f"Skipping item with invalid price: {item_name}, {item_value}")
            continue

        quantity = int(item.get("item_quantity", 1))
        transaction_date = extracted_data.get("date", "Unknown Date")

        print(f"Inserting: {item_name}, {cost}, {quantity}, {transaction_date}")
        
        cursor.execute('''
            INSERT INTO Transactions (item_name, cost, quantity, transaction_date)
            VALUES (?, ?, ?, ?)
        ''', (item_name, cost, quantity, transaction_date))
        conn.commit()

def clear_table():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM Transactions')
    conn.commit()

    cursor.execute('DELETE FROM sqlite_sequence WHERE name="Transactions"')
    conn.commit()

    print("Transactions table cleared and auto-increment reset.")

    conn.close()


def query_database(cursor):
    cursor.execute('SELECT * FROM Transactions')
    rows = cursor.fetchall()
    print("Contents of Transactions Table:")
    for row in rows:
        print(row)
