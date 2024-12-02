import sqlite3
import json

class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name  # Manteniamo il nome del database
        self.conn = sqlite3.connect(self.db_name, timeout=10)  # Timeout per evitare blocchi
        self.create_tables()

    def create_tables(self):
        with self.conn:
            cursor = self.conn.cursor()

            # PCB Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS PCB (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                PCBTypeName TEXT
            )
            """)

            # Test Results Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Test_Results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pcb_id INTEGER,
                test_sequence TEXT,
                strategy_name TEXT,
                total_time REAL,
                profit REAL
            )
            """)

            # Component Probabilities Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Component_Probabilities (
                pcb_id INTEGER,
                component_id INTEGER,
                defect_name TEXT,
                probability REAL,
                PRIMARY KEY (pcb_id, component_id, defect_name)
            )
            """)

            # Test Execution Log Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Test_Execution_Log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pcb_id INTEGER,
                test_id INTEGER,
                observed_state TEXT,
                duration REAL,
                result TEXT
            )
            """)

            # Strategy Log Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Strategy_Log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pcb_id INTEGER,
                strategy_id INTEGER,
                final_state TEXT,
                profit REAL
            )
            """)

    def insert_test_result(self, pcb_id, test_sequence, strategy_name, total_time, profit):
        """
        Inserts a record into the Test_Results table.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO Test_Results (pcb_id, test_sequence, strategy_name, total_time, profit)
            VALUES (?, ?, ?, ?, ?)
            """, (pcb_id, test_sequence, strategy_name, total_time, profit))

    def insert_test_execution_log(self, pcb_id, test_id, observed_state, duration, result):
        """
        Inserts a record into the Test_Execution_Log table.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO Test_Execution_Log (pcb_id, test_id, observed_state, duration, result)
            VALUES (?, ?, ?, ?, ?)
            """, (pcb_id, test_id, observed_state, duration, result))

    def insert_strategy_log(self, pcb_id, strategy_id, final_state, profit):
        """
        Inserts a record into the Strategy_Log table.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO Strategy_Log (pcb_id, strategy_id, final_state, profit)
            VALUES (?, ?, ?, ?)
            """, (pcb_id, strategy_id, final_state, profit))

    def insert_probabilities(self, pcb_id, component_id, defect_name, probability):
        """
        Inserts or updates a record in the Component_Probabilities table.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO Component_Probabilities (pcb_id, component_id, defect_name, probability)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(pcb_id, component_id, defect_name)
            DO UPDATE SET probability = excluded.probability
            """, (pcb_id, component_id, defect_name, probability))
