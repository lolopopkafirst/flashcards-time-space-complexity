import sqlite3

class AlgoManager:
    def __init__(self, db_name="algo_vault.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def get_random_solution(self, table_name="all_solutions"):
        cursor = self.conn.cursor()
        # random task from db
        cursor.execute(f"SELECT title, code, time_complexity, space_complexity FROM {table_name} ORDER BY RANDOM() LIMIT 1")
        return cursor.fetchone()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Base schema for the specific tables
        schema = '''
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title text UNIQUE NOT NULL,
            code TEXT,
            time_complexity TEXT,
            space_complexity TEXT,
            date_solved TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        '''
        
        # 1. Master Table (Includes a status flag)
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS all_solutions (
                {schema},
                is_correct BOOLEAN
            )
        ''')
        
        # 2. Good Table
        cursor.execute(f"CREATE TABLE IF NOT EXISTS good_solutions ({schema})")
        
        # 3. Bad Table (Includes notes)
        cursor.execute(f"CREATE TABLE IF NOT EXISTS bad_solutions ({schema}, notes TEXT)")
        
        self.conn.commit()

    def add_solution(self, is_good, title, code, time, space, notes=None):
        cursor = self.conn.cursor()
        
        # --- 1. Insert into the Master Table ---
        master_query = '''
            INSERT INTO all_solutions (title, code, time_complexity, space_complexity, is_correct)
            VALUES (?, ?, ?, ?, ?)
        '''
        cursor.execute(master_query, (title, code, time, space, 1 if is_good else 0))

        # --- 2. Insert into Specific Tables ---
        if is_good:
            query = "INSERT INTO good_solutions (title, code, time_complexity, space_complexity) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (title, code, time, space))
        else:
            query = "INSERT INTO bad_solutions (title, code, time_complexity, space_complexity, notes) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(query, (title, code, time, space, notes))
            
        self.conn.commit()

    def get_stats(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM all_solutions")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM good_solutions")
        good = cursor.fetchone()[0]
        

# --- Example Usage ---
if __name__ == "__main__":
    vault = AlgoManager()
    vault.get_stats()