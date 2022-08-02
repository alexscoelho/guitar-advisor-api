from sqlalchemy.orm import Session
from typing import List, Union

from fastapi import HTTPException
from . import models, schemas

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    
    return db.query(models.User).filter(models.User.username == username).first()

def create_guitar(db: Session, guitar: schemas.GuitarCreate):
    db_guitar = models.Guitar(price=guitar.price, name=guitar.name, brand=guitar.brand, description=guitar.description, manufacturer_country=guitar.manufacturer_country, image_url=guitar.image_url)
    db.add(db_guitar)
    db.commit()
    db.refresh(db_guitar)
    return db_guitar

def get_guitars(db: Session, skip: int = 0, limit: int = 100, q: Union[str, None] = None):
    if q:
        guitars = db.query(models.Guitar).filter(models.Guitar.brand==q).all()
        return guitars
    guitars = db.query(models.Guitar).offset(skip).limit(limit).all()
    return guitars

def get_guitar(db: Session, guitar_id: int):
    return db.query(models.Guitar).filter(models.Guitar.id == guitar_id).first()

def delete_guitar(db: Session, guitar_id: int):
    db_guitar = db.query(models.Guitar).filter(models.Guitar.id == guitar_id).delete()
    if db_guitar == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    db.commit()
    return {"guitar_deleted": guitar_id}

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
