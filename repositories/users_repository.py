from database import get_db_connection
from models import User
from auth import get_password_hash


class UsersRepository:
    def __init__(self):
        self.conn = get_db_connection()
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                    )
            ''')

    def add_user(self, user):
        with self.conn:
            self.conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (user.username, hashed_password))

    def get_user_by_username(self, username):
        user = self.conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        return user
