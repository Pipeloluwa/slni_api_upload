from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .import token

oauth2_scheme= OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token_: str= Depends(oauth2_scheme)):
    credentials_exception= HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= "Could not validate your login details",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token.verify_token(token_,credentials_exception)