import os
from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import models
from database import get_db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY","fallback_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes =["bcrypt"], deprecated = "auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(password: str):
    truncated = password.encode("utf-8")[:72]
    return pwd_context.hash(truncated)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token:str= Depends(oauth2_scheme), db : Session= Depends(get_db)):
    credential_exception= HTTPException(
        status_code=404,
        detail= "Could not validate cerdential",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload= jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username:str = payload.get("sub")
        if username is None:
            raise credential_exception
    except JWTError:
        raise credential_exception

    user = db.query(models.Developer).filter(models.Developer.username == username).first()
    if user is None:
        raise credential_exception

    return user