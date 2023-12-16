from .. import models
from ..hashing import Hash
from ..routers import otp_management
from fastapi import HTTPException, status, Response
import time
import os
from dotenv import load_dotenv
load_dotenv()



async def add_teachers(request, db, username):
    if not db.query(models.Admin).filter(models.Admin.username==username).first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)
    
    if request.username == os.getenv('ADMIN_USER'):
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail="this username is already taken")
    check_username= db.query(models.Users).filter(models.Users.username==request.username.lower()).first()
    check_useremail= db.query(models.Users).filter(models.Users.email==request.email.lower()).first()
    if check_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="this username is already taken")
    if check_useremail:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="this email is already taken")
    new_user= models.Users(username=request.username.lower(),
                          role= "teacher",
                          email= request.email.lower(),
                          password= Hash.enc(request.password)
                          )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    get_user_id= db.query(models.Users).filter(models.Users.username==request.username).first().id
    teacher_profile= models.Profile(
        firstname= request.firstname,
        lastname= request.lastname,
        username= request.username.lower(),
        email= request.email.lower(),
        role= "teacher",
        users_id= get_user_id
    )

    db.add(teacher_profile)
    db.commit()
    db.refresh(teacher_profile)
    return new_user


async def view_teachers(db, username):
    if not db.query(models.Admin).filter(models.Admin.username==username).first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)
    return db.query(models.Profile).filter(models.Profile.role== 'teacher').all()


async def view_teachers_by_id(id, db, username):
    if not db.query(models.Admin).filter(models.Admin.username==username).first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)

    get_teachers_id= db.query(models.Users).filter(models.Users.id==id)
    if not get_teachers_id.first() or get_teachers_id.first().role == 'student':
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Teacher with this id '{id}' does not exist or has been removed")
    return get_teachers_id.first()


async def update_teachers(id, request, db, username):
    if not db.query(models.Admin).filter(models.Admin.username==username).first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)
     
    get_teachers_id= db.query(models.Profile).filter(models.Profile.users_id==id)
    if not get_teachers_id.first() or get_teachers_id.first().role == 'student':
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Teacher with this id '{id}' does not exist or has been removed")

    update_teacher= {
                    "firstname": request.firstname,
                    "lastname": request.lastname,
                    "phone_no": request.phone_no,
                    "skill_occupation": request.skill_occupation,
                    "biography": request.biography
                    }

    get_teachers_id.update(update_teacher)
    db.commit()
    return update_teacher 
    

async def delete_teachers(id, db, username):
    if not db.query(models.Admin).filter(models.Admin.username==username).first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)

    get_teachers_id= db.query(models.Profile).filter(models.Profile.users_id==id)
    get_user_teachers_id= db.query(models.Users).filter(models.Users.id==id)
    teacher_everything= db.query(models.Total_Teacher_Everything).filter(models.Total_Teacher_Everything.teachers_id== id)
    if not get_teachers_id.first() or not get_user_teachers_id.first() or get_teachers_id.first().role == 'student':
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Teacher with this id '{id}' does not exist or it has been already removed")
    
    if teacher_everything.first():
        teacher_everything.delete(synchronize_session= False)
        db.commit()
    get_teachers_id.delete(synchronize_session= False), get_user_teachers_id.delete(synchronize_session= False)
    db.commit()


async def view_courses(db, username):
    if not db.query(models.Admin).filter(models.Admin.username==username).first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)
    return db.query(models.CoursesTags).all()


async def view_course_by_tag(tag, db, username):
    if not db.query(models.Admin).filter(models.Admin.username==username).first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)
    
    if not db.query(models.CoursesTags).filter(models.CoursesTags.id== tag).first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f'Course with this {tag} is not available')
    return db.query(models.CoursesTags).filter(models.CoursesTags.id== tag).first()
