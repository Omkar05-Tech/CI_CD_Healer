from jose import JWTError, jwt  
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from app.db.schemas import TokenData

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") or "abc"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 210

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")  # ✅ EXTRACTION: Get ID from token payload
        
        if username is None or user_id is None:
            raise credential_exception
            
        # ✅ ASSIGNMENT: Include the id in the TokenData object
        token_data = TokenData(username=username, id=user_id) 
    except JWTError as e:
        print("JWT error:", e)
        raise credential_exception
    
    return token_data