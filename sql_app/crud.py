from sqlalchemy.orm import Session

from . import models, schemas

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, username=user.username, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_guitar(db: Session, guitar: schemas.GuitarCreate):
    db_guitar = models.Guitar(price=guitar.price, name=guitar.name, brand=guitar.brand, description=guitar.description, manufacturer_country=guitar.manufacturer_country, image_url=guitar.image_url)
    db.add(db_guitar)
    db.commit()
    db.refresh(db_guitar)
    return db_guitar

def get_guitars(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Guitar).offset(skip).limit(limit).all()


def create_review(db: Session, review: schemas.ReviewCreate):
    db_review = models.Review(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review    

def create_like(db: Session, like: schemas.LikeCreate):
    db_like = models.Like(**like.dict())
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return db_like    
