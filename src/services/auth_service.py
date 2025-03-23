from sqlalchemy.orm import Session
from src.repositories.user_repository import UserRepository
from src.libs.security import hash_password, verify_password
from src.libs.jwt import create_access_token
from src.utils.error import AppError
from src.utils.message_code import MESSAGE_CODE

def register_user(db: Session, username: str, email: str, password: str):
    if UserRepository.get_user_by_username(db, username):
        raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Username already exists")

    if UserRepository.get_user_by_email(db, email):
        raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Email already exists")

    hashed_password = hash_password(password)
    user = UserRepository.create_user(db, username, email, hashed_password)
    return user

def authenticate_user(db: Session, email, password):
    user = UserRepository.get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise AppError(401, MESSAGE_CODE.UNAUTHORIZED, "Invalid credentials")

    token = create_access_token({"sub": {"name": user.username, "email": user.email, "id": user.id}})
    return {"access_token": token}
