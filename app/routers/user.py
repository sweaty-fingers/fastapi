from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # default 값 등을 넣어주기 위해 db에서 데이터를 가져와 인스턴스에 다시 넣어주는 작업
    return new_user


@router.get('/{id}', response_model=schemas.UserOut) 
def get_user(id: int, db: Session = Depends(get_db)):
    # id 하나만 필요하므로 first()를 사용해서 별도의 자원을 사용하는 것을 막는다.
    user = db.query(models.User).filter(models.User.id == id).first()
    
    # 유저가 존재하지 않을 시 에러처리
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")

    return user