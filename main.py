from fastapi import FastAPI, HTTPException, UploadFile, File
import shutil
import os
from pydantic import BaseModel
import sqlite3
import subprocess

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

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    upload_dir = os.path.join(os.path.dirname(__file__), 'images')
    os.makedirs(upload_dir, exist_ok = True)

    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = subprocess.run(["python3", "backend.py"], capture_output = True, text = True)

    if result.returncode != 0:
        return {"status": "error", "message": result. stderr}


    return {"status": "success", "filename": file.filename}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "127.0.0.1", port = 8000)