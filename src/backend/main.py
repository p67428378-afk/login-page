import os
from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from .database import SessionLocal, engine, Base, User, init_db

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

# Initialize database
@app.on_event("startup")
def on_startup():
    init_db()
    # For demonstration, create a default user if not exists
    db = SessionLocal()
    if not db.query(User).filter(User.username == "testuser").first():
        salt = pwd_context.generate_salt()
        hashed_password = pwd_context.hash("testpassword" + salt)
        db_user = User(username="testuser", hashed_password=hashed_password, salt=salt)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    db.close()

# CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Adjust as needed for your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Password hashing and verification
def verify_password(plain_password, hashed_password, salt):
    return pwd_context.verify(plain_password + salt, hashed_password)

def get_password_hash(password):
    salt = pwd_context.generate_salt()
    hashed_password = pwd_context.hash(password + salt)
    return hashed_password, salt

# OAuth2PasswordBearer for token-based authentication (optional, for future expansion)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Session Management (Simplified for HLD's open issue) ---
# In a real application, this would involve more robust session tokens (JWT) or server-side sessions.
# For now, we'll use a simple approach with a cookie.

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# --- API Endpoints ---

@app.post("/api/login")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password, user.salt):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create a session token (simplified for now)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    response.set_cookie(key="session_token", value=access_token, httponly=True, secure=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return {"message": "Login successful", "redirect_to": "/landing"}

@app.get("/api/logout")
async def logout(response: Response):
    response.delete_cookie(key="session_token")
    return {"message": "Logged out successfully"}

@app.get("/api/user")
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    payload = decode_access_token(session_token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token")
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token")
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
    return {"username": user.username}

# Serve static files for the frontend
app.mount("/", StaticFiles(directory="src/frontend", html=True), name="frontend")
