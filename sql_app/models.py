from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, Text, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime)

    liked_guitars = relationship("Like", back_populates="user_id")


class Guitar(Base):
    __tablename__ = "guitars"

    id = Column(Integer, primary_key=True, index=True)
    price = Column(BigInteger)
    name = Column(String)
    brand = Column(String)
    description = Column(Text)
    manufacturer_country = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime)

    reviews = relationship("Review", back_populates="guitar_id")
    likes = relationship("Like", back_populates="guitar_id")
    

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    num_stars = Column(Integer)
    text_body = Column(Text)
    created_at = Column(DateTime)

    guitar_id = Column(Integer, ForeignKey("guitars.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer)
    created_at = Column(DateTime)

    guitar_id = Column(Integer, ForeignKey("guitars.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
