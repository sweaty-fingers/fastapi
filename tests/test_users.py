from app import schemas
from .database import client, session #client가 session을 실행하므로 필요

def test_root(client):
    res = client.get("/", )
    print(res.json().get('message'))
    assert res.json().get('message') == 'Hello wwwwooorrlld change aaabbbb'
    assert res.status_code == 200


def test_create_user(client):
    # test코드에서는 /users뒤에 /를 붙여주지 않으면 /users/로 리디렉션이 이루어지지 않아서 에러가 발생한다.
    res = client.post("/users/", json={"email": "hello123@gmail.com", "password": "password123"})
    new_user = schemas.UserOut(**res.json()) # schemas에 필요한 요소들이 모두 포함되어 있는지 확인한다.
    assert new_user.email == "hello123@gmail.com"
    assert res.status_code == 201


def test_login_user(client):
    res = client.post(
        "/login", data={"username": "hello123@gmail.com", "password": "password123"}
    )
    assert res.status_code == 200
