from fastapi import APIRouter, Depends, status, UploadFile, File, Query, Body
from .. import schemas, database, oauth2
from sqlalchemy.orm import Session
from ..repositories import courses
from . import authentication
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional, Union, Annotated
import json

router= APIRouter(prefix="/course", tags= ["Courses"])
get_db= database.get_database




    
# async def my_dependency(id: str, about: str, category: str, level: str, price: str, material_includes: str, requirements: str, audience: str, sub_courses: str):
#     return {"id": id, "about": about, "category": category, "level": level, "price": price, "material_includes": material_includes, "requirements": requirements, "audience": audience, "sub_courses": sub_courses}


# # async def add(request: schemas.CourseRegister,file_video: UploadFile= File(...), file_pdf: Optional[UploadFile]= File(None), db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
#     return await courses.add(request, file_video, file_pdf, db, current_user.username)
#List[Union[UploadFile, str]]= File(None)
#file_pdfs: list[Union[UploadFile, str]] , request: Annotated[Union[List[str], None], Query(min_length=3)]= None
#cover_picture: UploadFile, file_pictures: list [UploadFile], file_videos: list[UploadFile], file_pdfs: Union[list[UploadFile], None]= None , request: schemas.CourseAllRegister= Depends()

# id: Annotated[Union[str, None], Query()]= None, about: Annotated[Union[str, None], Query()]= None, category: Annotated[Union[str, None], Query()]= None, \
#         level: Annotated[Union[str, None], Query()]= None, price: Annotated[Union[str, None], Query()]= None, material_includes: Annotated[Union[str, None], Query()]= None, \
#             requirements: Annotated[Union[str, None], Query()]= None, audience: Annotated[Union[str, None], Query()]= None, sub_courses: Annotated[Union[list[str], None], Query()]= None, \
#                 db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)
@router.post('/add', status_code= status.HTTP_201_CREATED)
async def add(cover_picture: Union[UploadFile, None]= None, file_pictures: list[Union[UploadFile, None]]= None, file_videos: list[Union[UploadFile, None]]= None, file_pdfs: list[Union[UploadFile, None]]= None, \
    request_body: Annotated[Union[str, None], Query()]= None, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    #restructure_request= json.dumps(request_body)
    #restructure_to_dict= json.loads(request_body)
    request_to_json= schemas.CourseAllRegister.parse_raw(request_body)
    return await courses.add(cover_picture, file_pictures, file_videos, file_pdfs, request_to_json, db, current_user.username)

@router.get('/view-tags', status_code=status.HTTP_200_OK, response_model= List[schemas.CoursesTags])
async def view_tags(db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await courses.view_tags(db, current_user.username)

@router.get('/view-by-tag/{tag}', status_code=status.HTTP_200_OK, response_model= schemas.CoursesTags)
async def view_by_tag(tag: str, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await courses.view_by_tag(tag, db, current_user.username)

@router.put('/update', status_code=status.HTTP_200_OK)
async def update(cover_picture: Union[UploadFile, None]= None, file_pictures: list[Union[UploadFile, None]]= None, file_videos: list[Union[UploadFile, None]]= None, file_pdfs: list[Union[UploadFile, None]]= None, \
    request_body: Annotated[Union[str, None], Query()]= None, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):

    request_to_json= schemas.CourseAllUpdate.parse_raw(request_body)
    return await courses.update(cover_picture, file_pictures, file_videos, file_pdfs, request_to_json, db, current_user.username)

# @router.put('/{tag}/update-tag', status_code=status.HTTP_200_OK)
# async def update_tag(tag: str, request: schemas.CourseTagRegister, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
#     return await courses.update_tag(tag, request, db, current_user.username)

@router.delete('/delete/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: str, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await courses.delete(id, db, current_user.username)

@router.delete('/delete-tag/{tag}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag: str, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await courses.delete_by_tag(tag, db, current_user.username)

@router.post('/add-quiz', status_code= status.HTTP_201_CREATED)
async def add_quiz(request: schemas.Quiz, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await courses.add_quiz(request, db, current_user.username)

@router.get('/view-quiz', status_code= status.HTTP_200_OK, response_model= List[schemas.QuizUmbrella])
async def view_quiz(db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await courses.view_quiz(db, current_user.username)

@router.get('/view-quiz-by-tag/{tag}', status_code= status.HTTP_200_OK, response_model= schemas.QuizUmbrella)
async def view_quiz_by_tag(tag: str, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await courses.view_quiz_by_tag(tag, db, current_user.username)

@router.delete('/remove-quiz/{tag}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_quiz(tag: str, options_id: List[schemas.QuizOptionID], db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await courses.remove_quiz(tag, options_id, db, current_user.username)


@router.get('/view-total-everything', status_code= status.HTTP_200_OK, response_model= schemas.TotalTeacherEverything)
async def view_total_everything(db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await courses.view_total_everything(db, current_user.username)

