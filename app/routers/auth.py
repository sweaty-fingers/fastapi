from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException, Response

from app.utils import verify
from app.database import get_db
from app.schemas import UserLogin
from app.models import User


router = APIRouter(tags=["Authentification"])

@router.post('/login')
def login(user_credentials: UserLogin,  db: Session = Depends(get_db)):
    """
    사용자의 로그인을 관리한다.
    아이디와 패스워드를 확인한 후 정보가 없거나 패스워드가 일치하지 않으면 invalid Credentials 예외를 반환한다.
    (추가적인 정보를 제한하기 위해 아이디와 패스워드 중 어느 것이 잘못되었는지 알리지 않는다.)
    """
  
    user = db.query(User).filter(User.email == user_credentials.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"invalid Credentials")
    
    if not verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"invalid Credentials")
    
    # create a token
    # return token
    return {"token": "example_token"}


