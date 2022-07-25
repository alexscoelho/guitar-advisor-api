from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, Text, DateTime
from sqlalchemy.orm import relationship
import datetime

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    liked_guitars = relationship("Like", back_populates="user")


class Guitar(Base):
    __tablename__ = "guitars"

    id = Column(Integer, primary_key=True, index=True)
    price = Column(BigInteger)
    name = Column(String)
    brand = Column(String)
    description = Column(Text)
    manufacturer_country = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    reviews = relationship("Review", back_populates="guitar")
    likes = relationship("Like", back_populates="guitar")
    

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    num_stars = Column(Integer)
    text_body = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    guitar_id = Column(Integer, ForeignKey("guitars.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    guitar = relationship("Guitar", back_populates="reviews")

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    guitar_id = Column(Integer, ForeignKey("guitars.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="liked_guitars")
    guitar = relationship("Guitar", back_populates="likes")
