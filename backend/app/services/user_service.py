from typing import List, Optional
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.database import db
from app.core.security import get_password_hash, verify_password
from datetime import datetime

class UserService:
    def create_user(self, user_data: UserCreate) -> User:
        hashed_password = get_password_hash(user_data.password)
        
        # Insertar usuario usando el contexto de conexión correcto
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insertar el usuario
            insert_query = """
            INSERT INTO USERS (USERNAME, EMAIL, HASHED_PASSWORD, IS_ACTIVE, ROLE, CREATED_AT, UPDATED_AT)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            now = datetime.now()
            params = (
                user_data.username,
                user_data.email,
                hashed_password,
                user_data.is_active,
                user_data.role if hasattr(user_data, 'role') and user_data.role else 'OPERADOR',
                now,
                now
            )
            
            cursor.execute(insert_query, params)
            
            # Obtener el ID generado usando el generador de Firebird
            cursor.execute("SELECT GEN_ID(GEN_USERS_ID, 0) FROM RDB$DATABASE")
            user_id = cursor.fetchone()[0]
            
            conn.commit()
        
        return User(
            id=user_id,
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=user_data.is_active,
            role=user_data.role if hasattr(user_data, 'role') else 'OPERADOR',
            created_at=now,
            updated_at=now
        )
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT ID, USERNAME, EMAIL, HASHED_PASSWORD, IS_ACTIVE, CREATED_AT, UPDATED_AT, ROLE FROM USERS WHERE ID = ?"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if result:
                return User(
                    id=result[0],
                    username=result[1],
                    email=result[2],
                    hashed_password=result[3],
                    is_active=result[4],
                    created_at=result[5],
                    updated_at=result[6],
                    role=result[7] if len(result) > 7 else 'OPERADOR'
                )
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT ID, USERNAME, EMAIL, HASHED_PASSWORD, IS_ACTIVE, CREATED_AT, UPDATED_AT, ROLE FROM USERS WHERE USERNAME = ?"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            
            if result:
                return User(
                    id=result[0],
                    username=result[1],
                    email=result[2],
                    hashed_password=result[3],
                    is_active=result[4],
                    created_at=result[5],
                    updated_at=result[6],
                    role=result[7] if len(result) > 7 else 'OPERADOR'
                )
            return None
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            # Usar sintaxis de Firebird para paginación
            query = f"SELECT FIRST {limit} SKIP {skip} ID, USERNAME, EMAIL, HASHED_PASSWORD, IS_ACTIVE, CREATED_AT, UPDATED_AT, ROLE FROM USERS ORDER BY ID"
            cursor.execute(query)
            results = cursor.fetchall()
            
            users = []
            for row in results:
                users.append(User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    hashed_password=row[3],
                    is_active=row[4],
                    created_at=row[5],
                    updated_at=row[6],
                    role=row[7] if len(row) > 7 else 'OPERADOR'
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
        
        if user_data.role is not None:
            update_fields.append("ROLE = ?")
            params.append(user_data.role)
        
        if update_fields:
            update_fields.append("UPDATED_AT = ?")
            params.append(datetime.now())
            params.append(user_id)
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                query = f"UPDATE USERS SET {', '.join(update_fields)} WHERE ID = ?"
                cursor.execute(query, tuple(params))
                conn.commit()
        
        return self.get_user_by_id(user_id)
    
    def delete_user(self, user_id: int) -> bool:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = "DELETE FROM USERS WHERE ID = ?"
            cursor.execute(query, (user_id,))
            rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected > 0
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.get_user_by_username(username)
        if user and verify_password(password, user.hashed_password):
            return user
        return None

user_service = UserService()