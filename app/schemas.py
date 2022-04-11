from os import access
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass
    

class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    
    # pydantic 모델은 기본적으로 딕셔너리 타입의 정보가 들어올 것이라고 생각한다.
    # 따라서 ORM 타입 데이터가 들어갈 것이라고 명시해주어야 정상적으로 변환시켜줄 수 있다.
    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str


# 아이디를 만든 후 사용자에게 password와 같은 값을 보여주지 않기 위한 respose_model
class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None



# class UpdatePost(PostBase): 
#     # 만약 유저에게 오직 publish만 수정할 수 있게 하고 싶다면 updatePost shema에서 title과 content를 삭제한다.
#     # create와 update에서 접근할 수 있는 데이터에 차이를 둘 수 있기 때문에 각 요청에 각 스키마를 지정해줄 수 있다.
#     title: str
#     content: str
#     published: bool


