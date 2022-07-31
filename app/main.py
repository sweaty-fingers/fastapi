from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#from sqlalchemy.orm import Session
from .database import engine
from .routers import post, user, auth, vote
from . import models
from .config import settings

# app이 시작될 때 model에 정의된 테이블을 database에 생성하는 코드 존재해도 코드 실행에는 문제가 없으나
# alembic을 사용하게 되면 불필요하다.xxx
# => 완성된 서버를 처음 시작할 때 데이터베이스에 table을 생성하기 위해서 필요하다!
#models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"] # ["https://www.google.com", "https://www.youtube.com"] # 접근을 허용할 도메인 리스트
# "*" 포함시 모든 도메인에서 접근 가능하다.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/") # http 매서드, path를 전해줌
def root():
    return {"message": "Hello wwwwooorrlld change aaabbbb"}