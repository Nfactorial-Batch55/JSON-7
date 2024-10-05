from sqlalchemy.orm import Session

from database import get_db_connection
from models import Flower


class FlowersRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS flowers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    color TEXT NOT NULL
                )
            ''')

    def add_flower(self, name: str, color: str):
        new_flower = Flower(name=name, color=color)
        self.db.add(new_flower)
        self.db.commit()
        self.db.refresh(new_flower)
        return new_flower.id

    def get_all_flowers(self):
        return self.db.query(Flower).all()

    def update_flower(self, flower_id: int, name: str, color: str):
        flower = self.db.query(Flower).filter(Flower.id == flower_id).first()
        if flower:
            flower.name = name
            flower.color = color
            self.db.commit()
            self.db.refresh(flower)
        return flower

    def delete_flower(self, flower_id: int):
        flower = self.db.query(Flower).filter(Flower.id == flower_id).first()
        if flower:
            self.db.delete(flower)
            self.db.commit()
        return flower