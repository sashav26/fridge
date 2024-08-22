from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class Transaction(BaseModel):
    item_name: str
    cost: float
    quantity: int
    transaction_date: str

def connect_db():
    conn = sqlite3.connect('inventory.db')
    return conn

@app.get("/transactions/")
def get_transactions():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Transactions')
    rows = cursor.fetchall()
    conn.close()
    return rows

@app.post("/transaction/")
def add_transaction(transaction: Transaction):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
                   INSERT INTO Transactions (item_name, cost, quantity, transaction_date)
                   VALUES (?,?,?,?)
                   ''', (transaction.item_name, transaction.cost, transaction.quantity, transaction.transaction_date))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/totals/")
def calculate_totals():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT SUM(cost * quantity) FROM Transactions')
    total_price = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(quantity) FROM Transactions')
    total_items = cursor.fetchone()[0]

    conn.close()

    return {"total_price": total_price, "total_items": total_items}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "127.0.0.1", port = 8000)