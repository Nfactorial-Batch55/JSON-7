from sqlalchemy.orm import Session

from database import get_db_connection
from models import Flower, User

class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_purchased(self, user_id: int, flower_id: int):
        purchased = Purchased(user_id=user_id, flower_id=flower_id)
        self.db.add(purchased)
        self.db.commit()
        self.db.refresh(purchased)
        return purchased


    def get_purchased(self, user_id: int):
        self.db.query(Purchased).filter(Purchased.user_id == user_id).all()