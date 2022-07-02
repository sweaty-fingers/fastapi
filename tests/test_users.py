from fastapi.testclient import TestClient
from app.main import app
from app import schemas

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.config import settings

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


# Dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_root():
    res = client.get("/", )
    print(res.json().get('message'))
    assert res.json().get('message') == 'Hello wwwwooorrlld change aaabbbb'
    assert res.status_code == 200


def test_create_user():
    res = client.post("/users/", json={"email": "hello123@gmail.com", "password": "password123"})
    new_user = schemas.UserOut(**res.json()) # schemas에 필요한 요소들이 모두 포함되어 있는지 확인한다.
    assert new_user.email == "hello123@gmail.com"
    assert res.status_code == 201