from fastapi import APIRouter, Depends, HTTPException, status, Form
from ..import database, models, token, schemas, database, oauth2
from sqlalchemy.orm import Session
from ..hashing import Hash
from fastapi.security import OAuth2PasswordRequestForm

router=APIRouter(tags=['Password_Management'])

@router.post('/change_password', status_code= status.HTTP_200_OK)
async def login(request_password: str= Form(...), new_password: str= Form(...), db: Session= Depends(database.get_database), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    user= db.query(models.Users).filter(models.Users.username== current_user.username)
    usermail= db.query(models.Users).filter(models.Users.email== current_user.username)
    if not user.first():
        user=usermail
    if not user.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= "Your session has either expire or account is no more active")
    if not Hash.verify(request_password, user.first().password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= "Your Old password is incorrect")
    
    user.update({'password': Hash.enc(new_password)})
    db.commit()