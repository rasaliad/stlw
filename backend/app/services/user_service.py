from typing import List, Optional
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.database import db
from app.core.security import get_password_hash, verify_password
from datetime import datetime

class UserService:
    def create_user(self, user_data: UserCreate) -> User:
        hashed_password = get_password_hash(user_data.password)
        
        query = """
        INSERT INTO USERS (USERNAME, EMAIL, HASHED_PASSWORD, IS_ACTIVE, CREATED_AT, UPDATED_AT)
        VALUES (?, ?, ?, ?, ?, ?)
        RETURNING ID
        """
        
        now = datetime.now()
        params = (
            user_data.username,
            user_data.email,
            hashed_password,
            user_data.is_active,
            now,
            now
        )
        
        result = db.execute_query(query, params)
        user_id = result[0][0] if result else None
        
        return User(
            id=user_id,
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=user_data.is_active,
            created_at=now,
            updated_at=now
        )
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        query = "SELECT * FROM USERS WHERE ID = ?"
        result = db.execute_query(query, (user_id,))
        
        if result:
            row = result[0]
            return User(
                id=row[0],
                username=row[1],
                email=row[2],
                hashed_password=row[3],
                is_active=row[4],
                created_at=row[5],
                updated_at=row[6]
            )
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        query = "SELECT * FROM USERS WHERE USERNAME = ?"
        result = db.execute_query(query, (username,))
        
        if result:
            row = result[0]
            return User(
                id=row[0],
                username=row[1],
                email=row[2],
                hashed_password=row[3],
                is_active=row[4],
                created_at=row[5],
                updated_at=row[6]
            )
        return None
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        query = "SELECT * FROM USERS ORDER BY ID OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        result = db.execute_query(query, (skip, limit))
        
        users = []
        for row in result:
            users.append(User(
                id=row[0],
                username=row[1],
                email=row[2],
                hashed_password=row[3],
                is_active=row[4],
                created_at=row[5],
                updated_at=row[6]
            ))
        return users
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        existing_user = self.get_user_by_id(user_id)
        if not existing_user:
            return None
        
        update_fields = []
        params = []
        
        if user_data.username is not None:
            update_fields.append("USERNAME = ?")
            params.append(user_data.username)
        
        if user_data.email is not None:
            update_fields.append("EMAIL = ?")
            params.append(user_data.email)
        
        if user_data.is_active is not None:
            update_fields.append("IS_ACTIVE = ?")
            params.append(user_data.is_active)
        
        if update_fields:
            update_fields.append("UPDATED_AT = ?")
            params.append(datetime.now())
            params.append(user_id)
            
            query = f"UPDATE USERS SET {', '.join(update_fields)} WHERE ID = ?"
            db.execute_query(query, tuple(params))
        
        return self.get_user_by_id(user_id)
    
    def delete_user(self, user_id: int) -> bool:
        query = "DELETE FROM USERS WHERE ID = ?"
        rows_affected = db.execute_query(query, (user_id,))
        return rows_affected > 0
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.get_user_by_username(username)
        if user and verify_password(password, user.hashed_password):
            return user
        return None

user_service = UserService()