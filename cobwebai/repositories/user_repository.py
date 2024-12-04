from sqlalchemy.orm import Session
from cobwebai.models import User 
from typing import List, Optional

class UsersRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.user_id == user_id).first()

    def get_all_users(self) -> List[User]:
        return self.db.query(User).all()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).one_or_none()

    def create_user(self, user_data: dict) -> User:
        new_user = User(**user_data)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def delete_user(self, user_id: int) -> None:
        user = self.db.query(User).filter(User.user_id== user_id).first()
        if user:
            self.db.delete(user)
            self.db.commit()
