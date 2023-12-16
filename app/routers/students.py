from fastapi import APIRouter, Depends, status, HTTPException
from .. import schemas, database, oauth2, models
from sqlalchemy.orm import Session
from ..repositories import students
from . import authentication
from fastapi.security import OAuth2PasswordRequestForm
from typing import List

router= APIRouter(prefix="/student", tags= ["Students"])
get_db= database.get_database



@router.get('/manual_verify_user',status_code= status.HTTP_200_OK)
def manual_verify(db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    if db.query(models.Users).filter(models.Users.username == current_user.username).filter(models.Users.role == "student").first() == None:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)


@router.post('/register', response_model= schemas.Info, status_code= status.HTTP_201_CREATED)
async def students_sign_up(request: schemas.SignUp, db: Session= Depends(get_db)):
    return await students.students_sign_up(request, db)

@router.get('/view-profile', response_model= schemas.ViewProfileStudents, status_code= status.HTTP_200_OK)
async def view_students(db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.view_profile(current_user.username, db)

@router.put('/update-students', response_model= schemas.UsersProfile, status_code= status.HTTP_200_OK)
async def update_students(request: schemas.UsersProfileForm, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.update_students(request, current_user.username, db)

@router.put('/toggle-activation', status_code= status.HTTP_200_OK)
async def toggle_activation(db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.toggle_activation(db, current_user.username)




@router.get('/raw-courses/view', status_code=status.HTTP_200_OK, response_model= List[schemas.AllCourseInfo])
async def raw_view_courses(db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.raw_view_courses(db, current_user.username)

@router.get('/{tag}/raw-view-course-by-tag', status_code=status.HTTP_200_OK, response_model= List[schemas.CourseTeacher])
async def raw_view_course_by_tag(tag: str, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.raw_view_course_by_tag(tag, db, current_user.username)


@router.get('/raw-tags', status_code=status.HTTP_200_OK, response_model= List[schemas.CoursesTags])
async def raw_tags(db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.raw_tags(db, current_user.username)


@router.get('/{tag}/add-course', status_code= status.HTTP_201_CREATED)
async def add_course(tag: str, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.add_course(tag, db, current_user.username)


@router.delete('/{tag}/delete_tag', status_code=status.HTTP_204_NO_CONTENT)
async def delete(tag: str, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.delete_by_tag(tag, db, current_user.username)


@router.get('/{tag}/buy-course', status_code= status.HTTP_201_CREATED)
async def buy_course(tag: str, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.buy_course(tag, db, current_user.username)

@router.get('/get-course', status_code= status.HTTP_200_OK, response_model= List[schemas.CourseStudent])
async def get_course(db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.get_course(db, current_user.username)

@router.get('/{tag}/get-course-by-tag', status_code= status.HTTP_200_OK, response_model=List[schemas.CourseStudent])
async def get_course_by_tag(tag: str, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.get_course_by_tag(tag, db, current_user.username)

@router.post('/{id}/add-review', status_code= status.HTTP_201_CREATED)
async def add_review(id: int, request: schemas.Review, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.add_review(id, request, db, current_user.username)




@router.post('/submit-answers', status_code= status.HTTP_201_CREATED)
async def submit_answers(request: List[schemas.QuizAnswer], db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.submit_answers(request, db, current_user.username)

@router.get('/{tag}/view-quiz', status_code= status.HTTP_200_OK, response_model= List[schemas.QuizUmbrella])
async def view_quiz(tag: str, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.view_quiz(tag, db, current_user.username)

@router.post('/create-quiz-total-result', status_code= status.HTTP_201_CREATED)
async def create_quiz_total_result(request: schemas.QuizTotalResult, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.create_quiz_total_result(request, db, current_user.username)

@router.get('/{tag}/view-quiz-total-result', status_code= status.HTTP_200_OK, response_model= schemas.ViewQuizTotalResult)
async def view_quiz_total_result(tag: str, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.view_quiz_total_result(tag, db, current_user.username)

@router.get('/view-all-quiz-total-result', status_code= status.HTTP_200_OK, response_model= List[schemas.ViewQuizTotalResult])
async def view_all_quiz_total_result(db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.view_all_quiz_total_result(db, current_user.username)


@router.get('/view-total-everything', status_code= status.HTTP_200_OK, response_model= schemas.Total_Students_Everything)
async def view_total_everything(db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    return await students.view_total_everything(db, current_user.username)
