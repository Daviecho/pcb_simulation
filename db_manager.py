# db_manager.py
import sqlite3
import time

class DatabaseManager:
    def __init__(self, savepath):
        self.path = savepath
        self.conn = sqlite3.connect(":memory:")  # Use in-memory database
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Table Test_Results with pcb_id AUTOINCREMENT and new state columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Test_Results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                progress REAL,
                pcb_id TEXT,
                test_sequence TEXT,
                total_time REAL,
                profit REAL,
                CumRew REAL,
                real_state TEXT,
                finalstate TEXT,
                observed_state TEXT
            )
        """)
        self.conn.commit()

    def insert_test_result(self, progress, pcb_id, test_sequence, total_time, profit, CumRew, real_state, finalstate, observed_state):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Test_Results (progress, pcb_id, test_sequence, total_time, profit, CumRew, real_state, finalstate, observed_state)
            VALUES (?, ?, ?, ?, ?, ?, ?,?,?)
        """, (progress, pcb_id,  test_sequence, total_time, profit, CumRew, real_state, finalstate, observed_state))
        self.conn.commit()

    def fetch_all_results(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Test_Results")
        return cursor.fetchall()

    def close(self):
        # Save in-memory database to disk
        with sqlite3.connect(self.path) as disk_conn:
            self.conn.backup(disk_conn)
        self.conn.close()
