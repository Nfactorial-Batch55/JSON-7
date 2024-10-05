from fastapi import FastAPI, Depends, HTTPException, status, Form, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import sqlite3
from typing import List, Optional

from sqlalchemy.orm import Session

from database import get_db_connection
from repositories.users_repository import UsersRepository
from repositories.flowers_repository import FlowersRepository, Flower
from repositories.cart_repository import CartRepository
from auth import authenticate_user, create_access_token

# Конфигурация
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Инициализация
app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Модель пользователя
class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserInDB(User):
    hashed_password: str

class FlowerCreate(BaseModel):
    name: str
    color: str

class FlowerUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


#main


@app.post("/signup")
def signup(user: User, db: Session = Depends(get_db_connection)):
    users_repository = UsersRepository(db)
    db_user = users_repository.get_user_by_username(user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    users_repository.create_user(user.username, user.password)
    return {"message": "User registered successfully"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_connection)):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/profile")
def read_profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_connection)):
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
    users_repository = UsersRepository(db)
    user = users_repository.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return {"username": user.username}

#flowers

@app.post('/flowers')
def add_flower(flower: FlowerCreate, db: Session = Depends(get_db_connection)):
    flowers_repository = FlowersRepository(db)
    flower_id = flowers_repository.add_flower(flower.name, flower.color)
    return {'id': flower_id}

@app.get('/flowers')
def get_flowers(db: Session = Depends(get_db_connection)):
    flowers_repository = FlowersRepository(db)
    flowers_repository = flowers_repository.get_all_flowers()
    return flowers

@app.patch('/flowers')
def update_flowers(flower_id: int, flower: FlowerUpdate, db: Session = Depends(get_db_connection)):
    flowers_repository = FlowersRepository(db)
    updated_flower = flowers_repository.update_flower(flower_id, flower.name, flower.color)
    if not updated_flower:
        raise HTTPException(status_code=404, detail='Updated')
    return updated_flower

@app.delete('/flowers')
def delete_flower(flower_id: int, db: Session = Depends(get_db_connection)):
    flowers_repository = FlowersRepository(db)
    deleted_flower = flowers_repository.delete_flower(flower_id)
    if not deleted_flower:
        raise HTTPException(status_code=404, delail='Flower not found')
    return {"message": "Flower deleted successfully"}


#cart

@app.post('/items')
def add_to_cart(flower_id: int = Form(), cart: Optional[str] = Cookie(None)):
    if cart:
        cart_items = cart.split(',')
    else:
        cart_items = []
    cart_items.append(str(flower_id))
    response = {'message': 'Flower added to cart'}
    response.set_cookie(key="cart", value=",".join(cart_items))
    return response

@app.get("/cart/items")
def get_cart_items(cart: Optional[str] = Cookie(None), db: Session = Depends(get_db_connection)):
    if cart:
        cart_items = cart.split(',')
    else:
        cart_items = []
    flower_repository = FlowersRepository(db)
    flowers = [flowers_repository.get_flower_by_id(int(flower_id)) for flower_id in cart_items]
    total_price = sum(flower["price"] for flower in flowers)
    return {"flowers": flowers, "total_price": total_price}


@app.post("/purchased")
def purchase_items(token: str = Depends(oauth2_scheme), cart: Optional[str] = Cookie(None)):
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
    user = get_user(username)
    if user is None:
        raise credentials_exception

    if cart:
        cart_items = cart.split(',')
    else:
        cart_items = []
    for flower_id in cart_items:
        cart_repository.add_purchased(user["id"], int(flower_id))
    response = {"message": "Flowers purchased successfully"}
    response.delete_cookie("cart")
    return response

@app.get("/purchased")
def get_purchased_items(token: str = Depends(oauth2_scheme)):
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
    user = get_user(username)
    if user is None:
        raise credentials_exception

    purchased_items = cart_repository.get_purchased(user["id"])
    flowers = [flowers_repository.get_flower_by_id(item["flower_id"]) for item in purchased_items]
    return {"flowers": flowers}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(main, host="0.0.0.0", port=8000)
