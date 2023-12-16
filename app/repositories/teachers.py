from .. import models
from ..hashing import Hash
from ..routers import otp_management
from .import s3Bucket
from fastapi import HTTPException, status, Response
import os
from dotenv import load_dotenv

load_dotenv()


async def view_profile(username, db):
    get_teachers_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_teachers_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_teachers_id.first().role == "student":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_teachers_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_teachers_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Teacher with this username: '{username}' does not exist or has been removed")

    return get_teachers_id.first()


async def update_teachers(request, file, username, db):
    get_teachers_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_teachers_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")

    if get_teachers_id.first().role == "student":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_teachers_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_teachers_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    get_teacher= db.query(models.Profile).filter(models.Profile.users_id== get_teachers_id.first().id)
    if not get_teacher.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")


    if file != None:
        bucket_folder_path= 'teacher/profile_picture'
        bucket_folder_path += f"/{get_teacher.first().users_id}"
        if get_teacher.first().profile_picture:
            # get_clean_file_name= f"{os.path.splitext(get_teacher.first().profile_picture)[0].split('/')[-1]}.jpg"
            # delete_object= await s3Bucket.s3_delete(get_clean_file_name, bucket_folder_path)
            get_url= await s3Bucket.s3_upload_replacement(file, get_teacher.first().profile_picture, bucket_folder_path, True)
            get_teacher.update({'profile_picture': f'{get_url}'})
            db.commit() 
        else:  
            get_url= await s3Bucket.s3_upload(file, bucket_folder_path, True)
            
            get_teacher.update({'profile_picture': f'{get_url}'})
            db.commit() 

    # +++++++ FILTERING OUT THE NONE FIELDS
    new_update_data= {}
    for i in request:
        if i[1] is not None:
            new_update_data.setdefault(i[0], i[1])

    if new_update_data:
        try:
            get_teacher.update(new_update_data)
            db.commit() 
        except:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "This email address is already taken, pleasse change the email address")
    

async def toggle_activation(db, username):
    get_teachers_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_teachers_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_teachers_id.first().activated == "false" and get_teachers_id.first().role != "admin":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if get_teachers_id.first().role == "student":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if not get_teachers_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    get_teacher= db.query(models.Profile).filter(models.Profile.users_id== get_teachers_id.first().id)
    toggle= "true"
    if get_teachers_id.first().activated== "true":
        toggle= "false"
    toggle_activation_update= {
        "activated": toggle
    }
    get_teachers_id.update(toggle_activation_update), get_teacher.update(toggle_activation_update)
    db.commit()

    if toggle== "false":
        return Response(content= f"The user with the id: {get_teachers_id.first().id} was deactivated successfuly")
    
    return Response(content= f"The user with the id: {get_teachers_id.first().id} was activated successfuly")
