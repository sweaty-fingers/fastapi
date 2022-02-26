from urllib import response
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()

#request Get method url: "/"

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


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


@app.get("/posts")
def get_posts():
    return {"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict["id"] = randrange(0, 1e6)
    my_posts.append(post_dict)
    return {"data": post_dict}
# title str, content str, category, Bool publish

# @app.get("/posts/latest") # "/posts/{id}" 뒤에 정의할 경우 앞서 정의한 {id}와 매치되어 에러가 뜰 수 있다.
# def get_latest_post():
#     post = my_posts[len(my_posts) - 1]
#     return {"detail": post}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} was not found")
        
        # response.status_code = status.HTTP_404_NOT_FOUND # status code를 404로 바꿈
        # return {'message': f"post with id: {id} was not found"}
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # deleting posts
    # array에서 요청한 ID에 해당하는 index 찾기
    # my_posts.pop(index)
    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
    my_posts.pop(index)
    # return {"message": "post was succesfully deleted"} # status_code로 204를 전달해준다면 아무것도 없다는 의미이므로 message를 return으로 보낼 경우 에러가 발생할 수 있다.
    return Response(status_code=status.HTTP_204_NO_CONTENT) 
 

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
    
    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[index] = post_dict
    return {"data": post_dict}
