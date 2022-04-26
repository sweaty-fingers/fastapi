from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas
from app.database import get_db
from app.oauth2 import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=['Posts']

)

@router.get("/", response_model=List[schemas.Post]) # 스키마의 리스트가 반환되어야 하므로 리스트 형이 아니라면 에러가 발생한다.
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(get_current_user),
limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # current_user의 타입은 int가 아니지만 앱 실행에 문제가 없다. 이를 Dict로 바꿔주어도 된다.
    # cursor.execute("""SELECT * FROM posts""") 
    # posts = cursor.fetchall()
    print(search)
    # posts = db.query(models.Post).all()
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    # 로그인 한 유저의 포스트만 보게 하는 법
    # posts = db.query(models.Post).filter(
    #     models.Post.owner_id == current_user.id).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    # f-string을 사용하게 되면 SQL명령어 등이 인자로 들어갈 때 구문이 실행되는 등 문제가 발생할 수 있다.
    # 따라서 SQL을 다룰 때에는 %s와 같은 형식을 사용한다.
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    
    print(current_user.email)
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit() 
    db.refresh(new_post) # default 값 등을 넣어주기 위해 db에서 데이터를 가져와 인스턴스에 다시 넣어주는 작업
    # db를 최신 상태로 유지해주는 작업
    return new_post
# title str, content str, category, Bool publish

# @router.get("/posts/latest") # "/posts/{id}" 뒤에 정의할 경우 앞서 정의한 {id}와 매치되어 에러가 뜰 수 있다.
# def get_latest_post():
#     post = my_posts[len(my_posts) - 1]
#     return {"detail": post}


@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
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
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    # deleting posts
    # array에서 요청한 ID에 해당하는 index 찾기
    # # my_posts.pop(index)

    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()
    # return {"message": "post was succesfully deleted"} # status_code로 204를 전달해준다면 아무것도 없다는 의미이므로 message를 return으로 보낼 경우 에러가 발생할 수 있다.
    return Response(status_code=status.HTTP_204_NO_CONTENT) 
 

@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()