import psycopg2
from psycopg2.extras import RealDictCursor

from fastapi import FastAPI, Response, status, HTTPException, Depends # Depends?
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import time

#from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

#request Get method url: "/"

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

# 데이터베이스 연결
while True:
    try:
        
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

@app.get("/") # http 매서드, path를 전해줌
def root():
    return {"message": "welcome to my root"}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    
    posts = db.query(models.Post).all() # all()을 붙이지 않으면 그냥 sql 구문이 된다.

    return {"data": posts}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""") 
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    # f-string을 사용하게 되면 SQL명령어 등이 인자로 들어갈 때 구문이 실행되는 등 문제가 발생할 수 있다.
    # 따라서 SQL을 다룰 때에는 %s와 같은 형식을 사용한다.
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post) # default 값 등을 넣어주기 위해 db에서 데이터를 가져와 인스턴스에 다시 넣어주는 작업
    return {"data": new_post}
# title str, content str, category, Bool publish

# @app.get("/posts/latest") # "/posts/{id}" 뒤에 정의할 경우 앞서 정의한 {id}와 매치되어 에러가 뜰 수 있다.
# def get_latest_post():
#     post = my_posts[len(my_posts) - 1]
#     return {"detail": post}


@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id),))
    # post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id).first() 
    # all()을 사용할 경우 특정 조건을 만족하는 모든 데이터를 찾으려 함. 
    # but id와 같은 pb를 사용할 경우 오직 하나의 데이터만 존재한다는 것을 알고 있음 => first()를 이용해서 처음에 찾아지는 하나만 이용

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} was not found")
        
        # response.status_code = status.HTTP_404_NOT_FOUND # status code를 404로 바꿈
        # return {'message': f"post with id: {id} was not found"}
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # deleting posts
    # array에서 요청한 ID에 해당하는 index 찾기
    # # my_posts.pop(index)

    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")

    post.delete(synchronize_session=False)
    db.commit()
    # return {"message": "post was succesfully deleted"} # status_code로 204를 전달해준다면 아무것도 없다는 의미이므로 message를 return으로 보낼 경우 에러가 발생할 수 있다.
    return Response(status_code=status.HTTP_204_NO_CONTENT) 
 

@app.put("/posts/{id}")
def update_post(id: int, updated_post: Post, db: Session = Depends(get_db)):
    
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
    
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return {"data": post_query.first()}
