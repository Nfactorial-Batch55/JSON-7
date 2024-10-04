from database import get_db_connection


class CartRepository:
    def __init__(self):
        self.conn = get_db_connection()
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS purchased (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    flower_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (flower_id) REFERENCES flowers (id)
                )
            ''')

    def add_purchased(self):
        with self.conn:
            self.conn.execute('INSERT INTO purchased (user_id, flower_id) VALUES (?, ?)', (user_id, flower_id))
            self.conn.commit()

    def get_purchased(self, user_id):
        cursor = self.conn.execute('SELECT * FROM purchased WHERE user_id = ?', (user_id,))
        purchased = cursor.fetchall()
        return [{"id": row["id"], "flower_id": row["flower_id"]} for row in purchased]