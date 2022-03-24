from urllib import response
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Response, status, HTTPException, Depends # Depends?
from fastapi.params import Body
from typing import Optional, List
from random import randrange
import time

from . import utils
#from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db

from .routers import post, user


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

#request Get method url: "/"

# 데이터베이스 연결
while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='postgres041$', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, {"title": "favorite foods", "content": "I like pizza", "id": 2}]

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p 

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


app.include_router(post.router)
app.include_router(user.router)

@app.get("/") # http 매서드, path를 전해줌
def root():
    return {"message": "welcome to my root"}