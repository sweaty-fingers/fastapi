from fastapi.testclient import TestClient
import pytest
from app.main import app

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.config import settings
from alembic import command

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# Dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

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
