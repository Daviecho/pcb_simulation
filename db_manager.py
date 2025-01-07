# db_manager.py
import sqlite3

class DatabaseManager:
    def __init__(self, db_name="database.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(":memory:")  # Use in-memory database
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Table Test_Results with pcb_id AUTOINCREMENT and new state columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Test_Results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pcb_id TEXT,
                test_sequence TEXT,
                total_time REAL,
                profit REAL,
                CumRew REAL,
                real_state TEXT,
                observed_state TEXT
            )
        """)
        self.conn.commit()

    def insert_test_result(self, pcb_id, test_sequence, total_time, profit, CumRew, real_state, observed_state):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Test_Results (pcb_id, test_sequence, total_time, profit, CumRew, real_state, observed_state)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (pcb_id, test_sequence, total_time, profit, CumRew, real_state, observed_state))
        self.conn.commit()

    def fetch_all_results(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Test_Results")
        return cursor.fetchall()

    def close(self):
        # Save in-memory database to disk
        with sqlite3.connect(self.db_name) as disk_conn:
            self.conn.backup(disk_conn)
        self.conn.close()
