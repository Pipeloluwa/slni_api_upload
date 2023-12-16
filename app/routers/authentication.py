from fastapi import APIRouter, Depends, HTTPException, status
from ..import database, models, token
from sqlalchemy.orm import Session
from ..hashing import Hash
from fastapi.security import OAuth2PasswordRequestForm

router=APIRouter(tags=['Authentication'])

@router.post('/login', status_code= status.HTTP_200_OK)

async def login(request:OAuth2PasswordRequestForm= Depends(), db: Session= Depends(database.get_database)):
    user= db.query(models.Users).filter(models.Users.username== request.username.lower()).first()
    usermail= db.query(models.Users).filter(models.Users.email== request.username.lower()).first()
    if not user:
        user=usermail
    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= "Check what you typed, because either the username or the email does not exist")
    if not Hash.verify(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= "Your password is incorrect")
    access_token= token.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
