from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/users/login")

def get_db() -> Generator:
    """Get database session."""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get current user from JWT token, or bypass if SKIP_AUTH=1."""
    print(f"SKIP_AUTH: {os.getenv('SKIP_AUTH')}")
    if os.getenv("SKIP_AUTH") == "1":
        print("Bypassing auth!")
        user = db.query(User).first()
        if not user:
            raise HTTPException(status_code=401, detail="No users in database for SKIP_AUTH bypass. Please create a user first.")
        return user
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    return user 