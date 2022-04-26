from fastapi import FastAPI
#from sqlalchemy.orm import Session
from .database import engine
from .routers import post, user, auth, vote
from . import models
from .config import settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/") # http 매서드, path를 전해줌
def root():
    return {"message": "welcome to my root"}