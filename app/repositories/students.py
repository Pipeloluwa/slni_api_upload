from .. import models
from ..hashing import Hash
from ..routers import otp_management
from fastapi import HTTPException, status, Response
import os
from dotenv import load_dotenv

load_dotenv()


async def students_sign_up(request, db):
    if request.username == os.getenv('ADMIN_USER'):
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail="this username is already taken")
    if db.query(models.Users).filter(models.Users.username==request.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="this username is already taken")
    if db.query(models.Users).filter(models.Users.email==request.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="this email is already taken")
    
    new_user= models.Users(username=request.username.lower(),
                          role= "student",
                          email= request.email.lower(),
                          password= Hash.enc(request.password)
                          )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    get_user_id= db.query(models.Users).filter(models.Users.username==request.username).first()

    student_profile= models.Profile(
        registration_date= get_user_id.registration_date,
        firstname= request.firstname,
        lastname= request.lastname,
        username= request.username.lower(),
        email= request.email.lower(),
        role= "student",
        users_id= get_user_id.id
    )
    
    
    db.add(student_profile)
    db.commit()
    db.refresh(student_profile)
    return new_user


async def view_profile(username, db):
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")

    return get_students_id.first()


async def update_students(request, username, db):
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")

    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    get_student= db.query(models.Profile).filter(models.Profile.users_id== get_students_id.first().id)
    if not get_student.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")


     #+++++++ FILTERING OUT THE NONE FIELDS
    new_update_data= {}
    for i in request:
        if i[1] is not None:
            new_update_data.setdefault(i[0], i[1])

    get_student.update(new_update_data)
    db.commit()
    return new_update_data 
    

async def toggle_activation(db, username):
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_students_id.first().activated == "false" and get_students_id.first().role != "admin":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    get_student= db.query(models.Profile).filter(models.Profile.users_id== get_students_id.first().id)
    toggle= "true"
    if get_students_id.first().activated== "true":
        toggle= "false"
    toggle_activation_update= {
        "activated": toggle
    }
    get_students_id.update(toggle_activation_update), get_student.update(toggle_activation_update)
    db.commit()

    if toggle== "false":
        return Response(content= f"The user with the id: {get_students_id.first().id} was deactivated successfuly")
    
    return Response(content= f"The user with the id: {get_students_id.first().id} was activated successfuly")









#import json
async def raw_view_courses(db, username):
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Your account has been removed")

    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    get_student= db.query(models.Profile).filter(models.Profile.users_id== get_students_id.first().id)
    if not get_student.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
        
    
    #db.query(models.QuizResult).filter(models.QuizResult.students_id == get_students_id.first().id).all()
    # return db.query(models.Courses).filter(models.Courses.students.contains()).all()
    return db.query(models.Courses).all()



async def raw_view_course_by_tag(tag: str, db, username):
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Your account has been removed")

    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    get_student= db.query(models.Profile).filter(models.Profile.users_id== get_students_id.first().id)
    if not get_student.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
        
        
    return db.query(models.Courses).filter(models.Courses.tags== tag).all()



async def raw_tags(db, username):
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Your account has been removed")

    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    get_student= db.query(models.Profile).filter(models.Profile.users_id== get_students_id.first().id)
    if not get_student.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
        
    return db.query(models.CoursesTags).all()


async def add_course(tag, db, username):
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Your account has been removed")

    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    get_student= db.query(models.Profile).filter(models.Profile.users_id== get_students_id.first().id)
    if not get_student.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    student= get_student.first().id
    course= models.StudentsCourse(students_id= student, course_tag=tag)
    db.add(course)
    db.commit()
    db.refresh(course)




async def delete_by_tag(tag, db, username):
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Your account has been removed")

    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    get_student= db.query(models.Profile).filter(models.Profile.users_id== get_students_id.first().id)
    if not get_student.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")


    courses= db.query(models.StudentsCourse).filter(models.StudentsCourse.course_tag== tag)
    if not courses.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Course with this tag: '{tag}' does not exist or has been removed")
    if courses.first().students_id != get_student.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Course with this tag: '{tag}' could not be matched with any of your course")
    if courses.filter(models.StudentsCourse.students_id == get_student.first().id).first().has_paid == 'true':
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= f"Course with this tag: '{tag}' has already been added, Sorry, this can no longer be deleted")

    
    courses.delete(synchronize_session= False)
    db.commit()




async def buy_course(tag, db, username):
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Your account has been removed")

    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    get_student= db.query(models.Profile).filter(models.Profile.users_id== get_students_id.first().id)
    if not get_student.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    

    course_model= db.query(models.CoursesTags).filter(models.CoursesTags.id== tag)
    if not (course_model.first()):
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Sorry, this course is not available or no longer exists")

    student_course_model= db.query(models.StudentsCourse).filter(models.StudentsCourse.students_id== get_students_id.first().id)
    student_course_model.update({'has_paid': 'true'})
    if not (course_model.first().total_enrolled):
        course_model.update({'total_enrolled': 1})
    else:
        course_model.update({'total_enrolled': int(course_model.first().total_enrolled) + 1})
    


    #+++++++++++++++ ADDING TOTAL NUMBERS +++++++++++++++++
    course_no= 0
    get_total_course_no= db.query(models.Total_Students_Everything).filter(models.Total_Students_Everything.students_id == get_students_id.first().id)
    total_everything_no= models.Total_Students_Everything(
        students_id= get_students_id.first().id,
        total_enrolled_no= course_no + 1
    )

    db.add(total_everything_no)
    db.commit()
    db.refresh(total_everything_no)


    course_no2= 0
    t_id= db.query(models.CoursesTags).filter(models.CoursesTags.id== tag).first().teacher_id
    get_total_course_no2= db.query(models.Total_Teacher_Everything).filter(models.Total_Teacher_Everything.teachers_id == t_id)
    course_no2= get_total_course_no2.first().total_enrolled_no
    total_everything_no2= {
        "total_enrolled_no" :  course_no2 + 1
    }

    get_total_course_no2.update(total_everything_no2)
    db.commit()

    


async def get_course(db, username):
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")

    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    get_student= db.query(models.Profile).filter(models.Profile.users_id== get_students_id.first().id)
    if not get_student.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    student= get_student.first().id
    course= db.query(models.StudentsCourse).filter(models.StudentsCourse.students_id== student).filter(models.StudentsCourse.has_paid== "true").all()
    return course


async def get_course_by_tag(tag, db, username):
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")

    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    get_student= db.query(models.Profile).filter(models.Profile.users_id== get_students_id.first().id)
    if not get_student.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    student= get_student.first().id
    course= db.query(models.StudentsCourse).filter(models.StudentsCourse.students_id== student).filter(models.StudentsCourse.course_tag== tag).filter(models.StudentsCourse.has_paid== "true")
    return course


async def add_review(id, request, db, username):
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")

    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    get_student= db.query(models.Profile).filter(models.Profile.users_id== get_students_id.first().id)
    if not get_student.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    student= get_student.first().id
    course= db.query(models.StudentsCourse).filter(models.StudentsCourse.students_id== student).filter(models.StudentsCourse.id== id)
    course.update({'student_review': request.review})
    db.commit()



async def submit_answers(request, db, username):
    result_value= "true"
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Your account has been removed")

    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    get_student= db.query(models.Profile).filter(models.Profile.users_id== get_students_id.first().id)
    if not get_student.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    

    if db.query(models.QuizResult).filter(models.QuizResult.students_id == get_students_id.first().id).filter(models.QuizResult.tag== request[0].tag).first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "You have already taken this quiz")
   

    for i in range (len(request)):
        questions= db.query(models.Quiz).filter(models.Quiz.id== request[i].question_id)
        if not questions.first():
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Course with this tag: '{request[i].question_id}' does not exist or has been removed")
        
        if request[i].student_answer != questions.first().answer:
            result_value= "false"
        student_answer= models.QuizStudents(student_answer= request[i].student_answer, quiz_id= request[i].question_id, tag= request[i].tag, students_id= get_students_id.first().id, result= result_value)
        db.add(student_answer)
        db.commit()
        db.refresh(student_answer)
        result_value= "true"



async def view_quiz(tag, db, username):
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Your account has been removed")

    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    get_student= db.query(models.Profile).filter(models.Profile.users_id== get_students_id.first().id)
    if not get_student.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    return db.query(models.QuizUmbrella).filter(models.QuizUmbrella.id == tag).all()



async def create_quiz_total_result(request, db, username):
    total_result= "true"
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Your account has been removed")

    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    


    passed_questions= db.query(models.QuizStudents).filter(models.QuizStudents.students_id == request.students_id).filter(models.QuizStudents.tag == request.tag).\
        filter(models.QuizStudents.result == "true").all()
    failed_questions= db.query(models.QuizStudents).filter(models.QuizStudents.students_id == request.students_id).filter(models.QuizStudents.tag == request.tag).\
        filter(models.QuizStudents.result == "false").all()
    if len(passed_questions) < len(failed_questions):
        total_result= "false"
    
    save_quiz_result= models.QuizResult(tag= request.tag, level= request.level, students_id= request.students_id, result= total_result)



    #+++++++++++++++ UPDATING THE TOTALS ++++++++++++++++++
    course_no= 0
    get_total_course_no= db.query(models.Total_Students_Everything).filter(models.Total_Students_Everything.students_id == get_students_id.first().id)
    if get_total_course_no.first():
        course_no= get_total_course_no.first().total_quiz_taken
        total_everything_no= {
            "total_quiz_taken" :  course_no + 1
        }

        if total_result == "true":
            get_quiz_umbrella= db.query(models.QuizUmbrella).filter(models.QuizUmbrella.id == request.tag)
            if get_quiz_umbrella.first():
                rating= 4
                if get_quiz_umbrella.first().difficulty.lower() == "intermediate":
                    rating= 7
                elif get_quiz_umbrella.first().difficulty.lower() == "advanced":
                    rating= 10
                student_rating=  {
                    'student_level_rating': get_total_course_no.first().student_level_rating + rating
                    }
                obtainable_rating= {
                    'obtainable_level_rating': get_total_course_no.first().obtainable_level_rating + 10
                    } 

        get_total_course_no.update(total_everything_no), get_total_course_no.update(student_rating), get_total_course_no.update(obtainable_rating)
        db.commit()       



        # +++++++++++TEACHERS UPDATE++++++++++++
        course_no2= 0
        t_id= db.query(models.CoursesTags).filter(models.CoursesTags.id== request.tag).first().teacher_id
        get_total_course_no2= db.query(models.Total_Teacher_Everything).filter(models.Total_Teacher_Everything.teachers_id == t_id)
        course_no2= get_total_course_no2.first().total_quiz_taken
        total_everything_no2= {
            "total_quiz_taken" :  course_no2 + 1
        }

        get_total_course_no2.update(total_everything_no2)
        db.commit()
        

    db.add(save_quiz_result)
    db.commit()
    db.refresh(save_quiz_result)



async def view_quiz_total_result(tag, db, username):
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Your account has been removed")

    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    # return 'download certificate'
    return db.query(models.QuizResult).filter(models.QuizResult.students_id== get_students_id.first().id).filter(models.QuizResult.tag == tag).first()



async def view_all_quiz_total_result(db, username):
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Your account has been removed")

    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    return db.query(models.QuizResult).filter(models.QuizResult.students_id== get_students_id.first().id).all()




async def view_total_everything(db, username):
    get_students_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_students_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Your account has been removed")

    if get_students_id.first().role == "teacher":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_students_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_students_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
   
   
    if not db.query(models.Total_Students_Everything).filter(models.Total_Students_Everything.students_id== get_students_id.first().id).first():
        return Response(status_code= status.HTTP_204_NO_CONTENT)
    return db.query(models.Total_Students_Everything).filter(models.Total_Students_Everything.students_id== get_students_id.first().id).first()
