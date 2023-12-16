from fastapi import APIRouter, Depends, status, HTTPException, UploadFile
from .. import schemas, database, oauth2, models
from sqlalchemy.orm import Session
from ..repositories import teachers
from . import authentication
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Union

router= APIRouter(prefix="/teacher", tags= ["Teachers"])
get_db= database.get_database


@router.get('/manual_verify_user',status_code= status.HTTP_200_OK)
def manual_verify(db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    if db.query(models.Users).filter(models.Users.username == current_user.username).filter(models.Users.role == "teacher").first() == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND)


@router.get('/view-profile', response_model= schemas.ViewProfileStudents, status_code= status.HTTP_200_OK)
async def view_teachers(db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await teachers.view_profile(current_user.username, db)

@router.put('/update-teachers', status_code= status.HTTP_200_OK) #, response_model= schemas.UsersProfile,
#request: Union [schemas.UsersProfileForm, None]= None, file: Union[UploadFile, None] = None,
async def update_teachers(file: Union[UploadFile, None] = None, request: schemas.UsersProfileForm= Depends() , db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await teachers.update_teachers(request, file, current_user.username, db)

@router.put('/toggle-activation', status_code= status.HTTP_200_OK)
async def toggle_activation(db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await teachers.toggle_activation(db, current_user.username)
