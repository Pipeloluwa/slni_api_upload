from .. import models
from ..hashing import Hash
from ..routers import otp_management
from fastapi import HTTPException, status, Response
import time
import os
from dotenv import load_dotenv
load_dotenv()

async def view_students(db, username):
    if not db.query(models.Admin).filter(models.Admin.username==username).first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)
    
    get_students_id= db.query(models.Users).filter(models.Users.role== 'student')
    # if not get_students_id.first():
    #     raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"No Students is available")
    return get_students_id.all()

async def view_students_by_id(id, db, username):
    if not db.query(models.Admin).filter(models.Admin.username==username).first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)

    get_students_id= db.query(models.Users).filter(models.Users.id==id)
    if not get_students_id.first() or get_students_id.first().role == 'teacher':
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this id '{id}' does not exist or has been removed")
    return get_students_id.first()

async def update_students(id, request, db, username):
    if not db.query(models.Admin).filter(models.Admin.username==username).first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)
     
    get_students_id= db.query(models.Profile).filter(models.Profile.users_id==id)
    if not get_students_id.first() or get_students_id.first().role == 'teacher':
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this id '{id}' does not exist or has been removed")

    update_student= {
                    "firstname": request.firstname,
                    "lastname": request.lastname,
                    "phone_no": request.phone_no,
                    "skill_occupation": request.skill_occupation,
                    "biography": request.biography
                    }

    get_students_id.update(update_student)
    db.commit()
    return update_student 
    
async def delete_students(id, db, username):
    if not db.query(models.Admin).filter(models.Admin.username==username).first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)

    get_students_id= db.query(models.Profile).filter(models.Profile.users_id==id)
    get_user_students_id= db.query(models.Users).filter(models.Users.id==id)
    get_students_user_id= db.query(models.StudentsCourse).filter(models.StudentsCourse.id==id)
    student_everything= db.query(models.Total_Students_Everything).filter(models.Total_Students_Everything.students_id== id)

    if not get_students_id.first() or not get_user_students_id.first() or get_students_id.first().role == 'teacher':
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this id '{id}' does not exist or it has been already removed")
    
    if student_everything.first():
        student_everything.delete(synchronize_session= False)
        db.commit()    
    get_students_id.delete(synchronize_session= False), get_user_students_id.delete(synchronize_session= False), get_students_user_id.delete(synchronize_session= False)
    db.commit()


async def toggle_activation(id, db, username):
    if not db.query(models.Admin).filter(models.Admin.username==username).first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)
    
    get_users_id= db.query(models.Users).filter(models.Users.id==id)
    if not get_users_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"User with this id '{id}' does not exist or has been removed")
    get_user= db.query(models.Profile).filter(models.Profile.users_id== get_users_id.first().id)

    toggle= "true"
    if get_users_id.first().activated== "true":
        toggle= "false"
    toggle_activation_update= {
        "activated": toggle
    }
    get_users_id.update(toggle_activation_update), get_user.update(toggle_activation_update)
    db.commit()

    if toggle== "false":
        return Response(content= f"The user with the id: {get_users_id.first().id} was deactivated successfuly")
    
    return Response(content= f"The user with the id: {get_users_id.first().id} was activated successfuly")


