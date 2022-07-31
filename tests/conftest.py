from fastapi.testclient import TestClient
import pytest
from app.main import app

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.config import settings
from alembic import command
from app import models
from app.oauth2 import create_access_token

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'


engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# app.dependency_overrides[get_db] = override_get_db
# client = TestClient(app)

# @pytest.fixture
# def client():
#     # TestClient를 반환하기 전 코드를 실행
#     Base.metadata.drop_all(bind=engine)
#     Base.metadata.create_all(bind=engine)
#     #command.upgrade("head")
#     yield TestClient(app)
#     # command.downgrade("base")
#     # run our code after our test finishes
#     # Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def session():
    print("my session fixture ran")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
# session과 client fixture를 나눔으로써 test 코드에 db를 별도로 넣어주어 테스트할 수 있게 되었다.

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


@pytest.fixture
def test_user2(client):
    """
    다른 유저의 데이터를 삭제하는 작업을 테스트 하기 위한 setup
    """
    user_data = {"email": "hello456@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    # response model이 schemas.UserOut이므로 password가 출력되지 않는다.
    # 따라서 password를 추가해준다.
    return new_user



@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})

@pytest.fixture
def authorized_client(client, token):
    """
    인증된 사용자가 필요한 test의 경우 기존 client 대신 사용
    client, token이 먼저 실행 -> athorized 실행
    """
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [{
        "title": "first title",
        "content": "first content",
        "owner_id": test_user['id']
    }, {
        "title": "2nd title",
        "content": "2nd content",
        "owner_id": test_user['id']
    },
        {
        "title": "3rd title",
        "content": "3rd content",
        "owner_id": test_user['id']
    }, {
        "title": "4th title",
        "content": "4th content",
        "owner_id": test_user2['id']
    }]


    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, posts_data)
    posts = list(post_map)
    session.add_all(posts)
    # session.add_all([models.Post(title="first", contest="first content", owner_id=test_user['id']),
    # models.Post(title="first", contest="first content", owner_id=test_user['id'])])
    
    session.commit()
    posts = session.query(models.Post).all()
    return posts
