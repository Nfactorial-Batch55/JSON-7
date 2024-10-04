from fastapi import Depends, HTTPException

from database import get_db_connection
from models import User
from auth import get_password_hash, oauth2_scheme

def get_password_hash():
    from auth import get_password_hash
    return get_password_hash()

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

def get_current_user(token: str = Depends(oauth2_scheme), users_repository: UsersRepository = Depends()):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = users_repository.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user