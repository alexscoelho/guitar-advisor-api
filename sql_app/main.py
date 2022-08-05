from hashlib import algorithms_available
from typing import List, Union
from datetime import datetime, timedelta
from pydantic import BaseSettings
import os
import time


from fastapi import Depends, FastAPI, HTTPException, status, Request, UploadFile, File, BackgroundTasks
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from . import crud, models, schemas
from .database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

class Settings(BaseSettings):
    cloud_name: str 
    api_key: str
    api_secret: str 
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    
    class Config:
        env_file = ".env"

settings = Settings()

# cloudinary
import cloudinary

cloudinary.config( 
  cloud_name = settings.cloud_name, 
  api_key = settings.api_key, 
  api_secret = settings.api_secret,
  secure = True
)

import cloudinary.uploader
import cloudinary.api



models.Base.metadata.create_all(bind=engine)

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session = Depends(get_db), username: str = "", password: str = "" ):
    user = crud.get_user_by_username(db, username = username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def generate_html_response():
    html_content = """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Hello World!!</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/", response_class=HTMLResponse)
async def root(request:Request):
    client_host = request.client.host
    name = os.getenv("MY_NAME", "World")
    print(f"Hello {name} from Python")
    print({"client_host": client_host})
    return generate_html_response()

def fake_decode_token(token):
    return schemas.UserBase(
        username=token + "fakedecoded", email="john@example.com"
    )

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.UserBase = Depends(get_current_user)):
    return current_user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}    
    


@app.post("/users/", response_model=schemas.User)
def sign_up(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/guitars/{guitar_id}", response_model=schemas.Guitar)
def read_guitar(guitar_id: int, db: Session = Depends(get_db)):
    db_guitar = crud.get_guitar(db, guitar_id=guitar_id)
    if db_guitar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guitar not found")
    return db_guitar


# @app.get("/guitars/", response_model=List[schemas.Guitar], dependencies=[Depends(get_current_user)])
@app.get("/guitars/", response_model=List[schemas.Guitar])
def read_guitars(q: Union[str, None] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):    
    guitars = crud.get_guitars(db, skip=skip, limit=limit, q=q)
    return guitars

@app.post("/guitars/", response_model=schemas.Guitar)
def create_guitar(guitar: schemas.GuitarCreate, db: Session = Depends(get_db)):
    return crud.create_guitar(db=db, guitar=guitar)

@app.delete("/guitars/{guitar_id}")
def delete_guitar(guitar_id: int, db: Session = Depends(get_db)):
    return crud.delete_guitar(db=db, guitar_id=guitar_id)

@app.post("/likes/", response_model=schemas.Like)
def create_like(like: schemas.LikeCreate, db: Session = Depends(get_db)):
    return crud.create_like(db=db, like=like)

@app.post("/reviews/", response_model=schemas.Review)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    return crud.create_review(db=db, review=review)

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


# Upload file
@app.post("/files/")
async def create_file(file: bytes = File()):
    data = cloudinary.uploader.upload(file)
    if "secure_url" not in data:
        raise HTTPException(status_code=404, detail="Image could not be uploaded")
    return {"secure_url": data["secure_url"]}

# middlewares
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    print("This is a middleware")
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(process_time)
    return response

# background tasks
def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)

@app.get("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}
