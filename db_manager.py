import sqlite3
import json

class DatabaseManager:
    def __init__(self, db_name="pcb_simulation.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Test_Results (
                pcb_id INTEGER PRIMARY KEY,
                test_sequence TEXT,
                strategy_used TEXT,
                total_time INTEGER,
                profit REAL
            )
        """)
        self.conn.commit()

    def insert_test_result(self, pcb_id, test_sequence, strategy_used, total_time, profit):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Test_Results (pcb_id, test_sequence, strategy_used, total_time, profit)
            VALUES (?, ?, ?, ?, ?)
        """, (pcb_id, test_sequence, strategy_used, total_time, profit))
        self.conn.commit()
