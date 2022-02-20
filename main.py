from fastapi import FastAPI

app = FastAPI()

#request Get method url: "/"

@app.get("/") # http 매서드, path를 전해줌
def root():
    return {"message": "welcome to my root"}


@app.get("/posts")
def get_posts():
    return {"data": "This is your posts"}


