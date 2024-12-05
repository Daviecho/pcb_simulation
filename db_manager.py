import sqlite3

class DatabaseManager:
    def __init__(self, db_name="database.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Tabella Test_Results con pcb_id AUTOINCREMENT
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Test_Results (
                pcb_id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_sequence TEXT,
                strategy_used TEXT,
                total_time REAL,
                profit REAL
            )
        """)
        self.conn.commit()

    def insert_test_result(self, test_sequence, strategy_used, total_time, profit):
        """
        Inserisce un nuovo risultato nella tabella Test_Results.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Test_Results (test_sequence, strategy_used, total_time, profit)
            VALUES (?, ?, ?, ?)
        """, (test_sequence, strategy_used, total_time, profit))
        self.conn.commit()

    def fetch_all_results(self):
        """
        Recupera tutti i record dalla tabella Test_Results.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Test_Results")
        return cursor.fetchall()
