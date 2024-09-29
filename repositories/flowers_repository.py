from database import get_db_connection

class Flower:
    def __init__(self, name, color):
        self.name = name
        self.color = color

class FlowersRepository:
    def __init__(self):
        self.conn = get_db_connection()
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS flowers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    color TEXT NOT NULL
                )
            ''')

    def add_flower(self, flower):
        with self.conn:
            cursor = self.conn.execute('INSERT INTO flowers (name, color) VALUES (?, ?)', (flower.name, flower.color))
            self.conn.commit()
            return cursor.lastrowid

    def get_all_flowers(self):
        cursor = self.conn.execute('SELECT * FROM flowers')
        flowers = cursor.fetchall()
        return [{"id": row["id"], "name": row["name"], "color": row["color"]} for row in flowers]
