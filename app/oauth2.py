from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from .schemas import TokenData
from . import database, models
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") # tokenUrl: 엔드포인트 주소

#Secret_key
#Algorithm
#Expriation time (없다면 사용자가 계속 로그인 한 상태로만 존재하게 된다.)

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60



def create_access_token(data: dict):
    """jwt access token을 만든다.
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # ?? utcnow? vs now
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    """
    jwt을 decode하고 validate한다. invalid 하면 지정된 에러메세지(credentials_exception)을 반환한다. 

    Args:
        token(str): jwt 토큰
        credentials_exception(_type_): 에러메세지
    
    Returns:
        schemas.TokenData: decode된 토큰 데이터
    """
    try:    
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)

    except JWTError:
        raise credentials_exception
    
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """토큰을 받아서 JWT를 검증하고 데이터를 반환한다.
       이 함수를 통해 토큰 검증하고 난 후 토큰을 이용하여 데이터베이스에 접근하여 데이터를 불러오는 작업을 함께 수행할 수 있다.
    """
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}) # (??) header?

    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user

