"""
SQLite এ orders table এ payment_method column যোগ করার migration script
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'database.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Column আছে কিনা চেক করা
cursor.execute("PRAGMA table_info(orders)")
columns = [col[1] for col in cursor.fetchall()]

if 'payment_method' not in columns:
    cursor.execute("ALTER TABLE orders ADD COLUMN payment_method VARCHAR DEFAULT 'cod'")
    conn.commit()
    print("✅ payment_method column যোগ হয়েছে!")
else:
    print("ℹ️ payment_method column আগে থেকেই আছে।")

conn.close()
