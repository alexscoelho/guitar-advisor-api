from typing import List, Union
from datetime import datetime

from pydantic import BaseModel

class ReviewBase(BaseModel):
    num_stars: str
    text_body: str
    guitar_id: int
    user_id: int

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class LikeBase(BaseModel):
    guitar_id: int
    user_id: int

class LikeCreate(LikeBase):
    pass

class Like(LikeBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class GuitarBase(BaseModel):
    price: int
    name: str
    brand: str
    description: str
    manufacturer_country: str
    image_url: str

class GuitarCreate(GuitarBase):
    pass

class Guitar(GuitarBase):
    id: int
    created_at: datetime
    reviews: List[Review] = []
    likes: List[Like] = []

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str
    username: str

class UserInDB(UserBase):
    hashed_password: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    liked_guitars: List[Like] = []

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None
    