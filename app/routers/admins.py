from fastapi import APIRouter, Depends, status, HTTPException
from .. import schemas, database, models, oauth2
from sqlalchemy.orm import Session
from ..repositories import teachers, admins_students, admins_teachers
from ..import oauth2
from typing import List
import os
from dotenv import load_dotenv
from ..hashing import Hash

load_dotenv()

router= APIRouter(prefix="/admin", tags= ["Admins"])
get_db= database.get_database


USERNAME= os.getenv('ADMIN_USER') ,
ROLE=  'admin' ,
EMAIL=  os.getenv('ADMIN_EMAIL'),
try:
    PASSWORD= Hash.enc(os.getenv('ADMIN_PASSWORD'))
except:
    pass

@router.get('/auto-create-admin', status_code= status.HTTP_201_CREATED)
async def auto_create_admin( db: Session= Depends(get_db)):
    if db.query(models.Admin).all():
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN)
    admin= models.Admin(username= USERNAME, role= ROLE, email= EMAIL)
    admin_as_user= models.Users(username= USERNAME, role= ROLE, email= EMAIL, password= PASSWORD)
    db.add(admin), db.add(admin_as_user)
    db.commit()
    db.refresh(admin), db.refresh(admin_as_user)

    profile= models.Profile(
        username= USERNAME,
        email= EMAIL,
        role= "admin",
        users_id= db.query(models.Users).filter(models.Users.username== USERNAME).first().id
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)


@router.get('/manual_verify_user',status_code= status.HTTP_200_OK)
def manual_verify(db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    if db.query(models.Users).filter(models.Users.username == current_user.username).filter(models.Users.role == "admin").first() == None:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)



@router.get('/view-students', response_model= List[schemas.ViewProfileStudents], status_code= status.HTTP_200_OK)
async def view_students( db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await admins_students.view_students(db, current_user.username)

@router.post('/view-students_by_id', response_model= schemas.ViewProfileStudents, status_code= status.HTTP_200_OK)
async def view_students(id: int,  db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await admins_students.view_students_by_id(id, db, current_user.username)

@router.put('/{id}/update-students', response_model= schemas.UsersProfile, status_code= status.HTTP_200_OK)
async def update_students(id: int, request: schemas.UsersProfileForm, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await admins_students.update_students(id, request, db, current_user.username)

@router.delete('/{id}/delete-students', status_code= status.HTTP_204_NO_CONTENT)
async def delete_students(id: int, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await admins_students.delete_students(id, db, current_user.username)




#TEACHER'S SECTION
@router.post('/register-teachers', response_model= schemas.Info, status_code= status.HTTP_201_CREATED)
async def add_teachers(request: schemas.SignUp, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await admins_teachers.add_teachers(request, db, current_user.username)

@router.get('/view-teachers', response_model= List[schemas.ViewProfile], status_code= status.HTTP_200_OK)
async def view_teachers( db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await admins_teachers.view_teachers(db, current_user.username)

@router.post('/view-teachers_by_id', response_model= schemas.ViewProfileStudents, status_code= status.HTTP_200_OK)
async def view_teachers(id: int,  db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await admins_teachers.view_teachers_by_id(id, db, current_user.username)

@router.put('/{id}/update-teachers', response_model= schemas.UsersProfile, status_code= status.HTTP_200_OK)
async def update_teachers(id: int, request: schemas.UsersProfile, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await admins_teachers.update_teachers(id, request, db, current_user.username)

@router.delete('/{id}/delete-teachers', status_code= status.HTTP_204_NO_CONTENT)
async def delete_teachers(id: int, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await admins_teachers.delete_teachers(id, db, current_user.username)

@router.put('/{id}/toggle-users-activation', status_code= status.HTTP_200_OK)
async def toggle_activation(id: int, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await admins_students.toggle_activation(id, db, current_user.username)

@router.get('/courses/view', status_code=status.HTTP_200_OK, response_model= List[schemas.CoursesTags])
async def view_courses(db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await admins_teachers.view_courses(db, current_user.username)

@router.get('/{tag}/view-course-by-tag', status_code=status.HTTP_200_OK, response_model= schemas.CoursesTags)
async def view_course_by_tag(tag: str, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await admins_teachers.view_course_by_tag(tag, db, current_user.username)
