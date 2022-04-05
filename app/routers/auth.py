from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app.utils import verify
from app.database import get_db
from app.schemas import UserLogin, Token
from app.models import User
from app.oauth2 import create_access_token


router = APIRouter(tags=["Authentification"])

@router.post('/login', response_model=Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(),  db: Session = Depends(get_db)):
    """
    사용자의 로그인을 관리한다.
    아이디와 패스워드를 확인한 후 정보가 없거나 패스워드가 일치하지 않으면 invalid Credentials 예외를 반환한다.
    (추가적인 정보를 제한하기 위해 아이디와 패스워드 중 어느 것이 잘못되었는지 알리지 않는다.)
    user_credenials: UserLogin 스키마를 사용하여 관리하는 것 보다 OAuth2PasswordRequestForm = Depends()을 사용하는 것이 편리하다.
    """
    # {"uesrname": "adfdsa", 
    #  "password": "afdfaasdf"}

    user = db.query(User).filter(User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"invalid Credentials")
    
    if not verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"invalid Credentials")
    
    # create a token
    # return token
    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


