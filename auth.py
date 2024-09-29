from datetime import datetime
from time import timezone

from cloudinit.util import deprecate
from debugpy.adapter import access_token
from dns.dnssectypes import Algorithm
from fastapi.security import OAuth2PasswordBearer
from nbformat.sign import algorithms
from passlib.context import CryptContext

from models import User
from repositories.users_repository import UsersRepository

SECRET_KEY = 'simplepass'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(users_repository: UsersRepository, username: str, password: str):
    user = users_repository.get_user_by_username(username)
    if not user:
        return Fasle
    if not verify_password(password, user['password']):
        return Fasle
    return user


