from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db_connection
from models import User
from auth import get_password_hash, oauth2_scheme

def get_password_hash():
    from auth import get_password_hash
    return get_password_hash()

class UsersRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str, password: str):
        hashed_password = get_password_hash(password)
        db_user = User(username=username, password=hashed_password)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

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