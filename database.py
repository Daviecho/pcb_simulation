import sqlite3

class DatabaseManager:
    def __init__(self, db_name="pcb_process.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        """Creates necessary tables in the database."""
        cursor = self.conn.cursor()

        # PCB Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS PCB (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Automatically increments IDs
            PCBTypeName TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")

        # Component Probabilities Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Component_Probabilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pcb_id INTEGER,
            component_id INTEGER,
            defect_name TEXT,
            probability REAL,
            UNIQUE(pcb_id, component_id, defect_name),
            FOREIGN KEY (pcb_id) REFERENCES PCB(id)
        )""")

        # Test Results Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Test_Results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pcb_id INTEGER,
            test_sequence TEXT,
            strategy_name TEXT,
            sequence_cost REAL,
            sequence_income REAL,
            profit REAL,
            FOREIGN KEY (pcb_id) REFERENCES PCB(id)
        )""")

        self.conn.commit()

    def insert_pcb(self, pcb_type_name):
        """Inserts a PCB record into the database and returns its ID."""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO PCB (PCBTypeName)
        VALUES (?)
        """, (pcb_type_name,))
        self.conn.commit()
        return cursor.lastrowid  # Returns the ID of the inserted PCB

    def insert_probabilities(self, pcb_id, component_id, defect_name, probability):
        """Inserts defect probabilities for a PCB component."""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO Component_Probabilities (pcb_id, component_id, defect_name, probability)
        VALUES (?, ?, ?, ?)
        """, (pcb_id, component_id, defect_name, probability))
        self.conn.commit()

    def insert_test_result(self, pcb_id, test_sequence, strategy_name, sequence_cost, sequence_income, profit):
        """Inserts a new test result for a PCB."""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO Test_Results (pcb_id, test_sequence, strategy_name, sequence_cost, sequence_income, profit)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (pcb_id, test_sequence, strategy_name, sequence_cost, sequence_income, profit))
        self.conn.commit()
