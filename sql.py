import sqlite3
from database import query_database, clear_table

def main():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    query_database(cursor)
    conn.close()

if __name__ == "__main__":
    main()
