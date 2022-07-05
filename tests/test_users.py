import pytest
from app import schemas
from jose import jwt
from .database import client, session #client가 session을 실행하므로 필요
from app.config import settings

@pytest.fixture
def test_user(client):
    user_data = {"email": "hello123@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    # response model이 schemas.UserOut이므로 password가 출력되지 않는다.
    # 따라서 password를 추가해준다.
    return new_user

# def test_root(client):
#     res = client.get("/", )
#     print(res.json().get('message'))
#     assert res.json().get('message') == 'Hello wwwwooorrlld change aaabbbb'
#     assert res.status_code == 200

def test_create_user(client):
    # test코드에서는 /users뒤에 /를 붙여주지 않으면 /users/로 리디렉션이 이루어지지 않아서 에러가 발생한다.
    res = client.post("/users/", json={"email": "hello123@gmail.com", "password": "password123"})
    new_user = schemas.UserOut(**res.json()) # schemas에 필요한 요소들이 모두 포함되어 있는지 확인한다.
    assert new_user.email == "hello123@gmail.com"
    assert res.status_code == 201


def test_login_user(client, test_user):
    res = client.post(
        "/login", data={"username": test_user['email'], "password": test_user["password"]}
    )
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")

    assert id == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200
