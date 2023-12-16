from .. import models
from .. import schemas
from ..hashing import Hash
from ..routers import otp_management
from fastapi import HTTPException, status, Response
from sqlalchemy import asc, desc
from sqlalchemy.orm import joinedload
# from pydantic import parse_obj_as, parse
import time
import os
from .import s3Bucket
from dotenv import load_dotenv
load_dotenv()


# async def add(request, file_video, file_pdf, db, username):
async def add(cover_picture, file_pictures, file_videos, file_pdfs, request, db, username):
    cover_picture_var= ""
    file_pictures_list= []
    file_videos_list= []
    file_pdfs_list= {}

 
    get_teacher_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_teacher_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_teacher_id.first().role == "student":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")
    
    if get_teacher_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_teacher_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Students with this username: '{username}' does not exist or has been removed")
    
    if db.query(models.CoursesTags).filter(models.CoursesTags.id == request.id.title()).first():
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail= "A Course with this unique title already exists, please, provide a new unique title")


    # +++++++ COVER PICTURE UPLOAD +++++++
    bucket_folder_path= f'teacher/courses/{request.id.title()}/cover_picture'
    get_url= await s3Bucket.s3_upload(cover_picture, bucket_folder_path, True)
    cover_picture_var= get_url

    # ++++++++ FILE PICTURES UPLOAD ++++++++
    for i in file_pictures:
        bucket_folder_path= f'teacher/courses/{request.id.title()}/file_picture'
        get_url= await s3Bucket.s3_upload(i, bucket_folder_path, True)
        file_pictures_list.append(get_url)
    
    # ++++++++ FILE VIDEOS UPLOAD ++++++++
    for i in file_videos:
        bucket_folder_path= f'teacher/courses/{request.id.title()}/file_video'
        get_url= await s3Bucket.s3_upload(i, bucket_folder_path, False)
        file_videos_list.append(get_url)
    
    # ++++++++ FILE PDFS UPLOAD ++++++++
    if file_pdfs != None:
        for i in file_pdfs:
            bucket_folder_path= f'teacher/courses/{request.id.title()}/file_pdf'
            get_url= await s3Bucket.s3_upload(i, bucket_folder_path, False)
            # file_pdfs_list.setdefault(os.path.splitext(i.filename)[0].replace(" ", ""), get_url) #REMOVING THE WHITE SPACE FROM EVERY PLACE IN A STRING
            file_pdfs_list.setdefault(os.path.splitext(i.filename)[0], get_url)


    # ++++++++ SAVING THE COURSE TAG GENERAL +++++++++++
    new_course_tag= models.CoursesTags(
        id= request.id.title(),
        about= request.about,
        category= request.category,
        level= request.level,
        price= request.price,
        material_includes= request.material_includes,
        requirements= request.requirements,
        audience= request.audience,
        teacher_id= get_teacher_id.first().id,
        cover_picture= cover_picture_var
    )

    # ++++++++++ HANDLING TEACHER EVERYTHING +++++++++++
    course_no= 0
    get_total_course_no= db.query(models.Total_Teacher_Everything).filter(models.Total_Teacher_Everything.teachers_id == get_teacher_id.first().id)
    if get_total_course_no.first():
        course_no= get_total_course_no.first().total_course_no
        total_everything_no= {
            "total_course_no" :  course_no + 1
        }

        get_total_course_no.update(total_everything_no)
        db.commit()

    else:
        total_everything_no= models.Total_Teacher_Everything(
            teachers_id= get_teacher_id.first().id,
            total_course_no= course_no + 1
        )
        db.add(total_everything_no)
        db.commit()
        db.refresh(total_everything_no)

    db.add(new_course_tag)
    db.commit()
    db.refresh(new_course_tag)
    #+++++++++++++++ ENDED +++++++++++++++++++


    # ++++++++++ ADDING THE SUB COURSES +++++++++++++++
    for i in range (len(request.sub_courses)):
        try:
            new_course= models.Courses(
                                title= request.sub_courses[i].title.title(),
                                cover_picture= file_pictures_list[i],
                                video= file_videos_list[i],
                                pdf= file_pdfs_list[request.sub_courses[i].title],
                                tags= request.id.title(),
                                teacher_id= get_teacher_id.first().id
                                )
        except:
            new_course= models.Courses(
                                title= request.sub_courses[i].title.title(),
                                cover_picture= file_pictures_list[i],
                                video= file_videos_list[i],
                                tags= request.id.title(),
                                teacher_id= get_teacher_id.first().id
                                )
        db.add(new_course)
        db.commit()
        db.refresh(new_course)



async def view_tags(db, username):
    get_teacher_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_teacher_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_teacher_id.first().role == "student":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_teacher_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_teacher_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Teacher with this username: '{username}' does not exist or has been removed")
    
    # +++++++ PARSING OBJECTS TO RESTRUCTURE THE RESPONSE MODEL BY SUBSTITUTING A PREFFERED LINK FROM S3 BUCKET FOR THE NAME OF THE FILE STORE IN THE DB 
    # query_sub_courses= db.query(models.Courses).order_by(asc(models.Courses.id)).all()
    courses_object= db.query(models.Courses).filter(models.Courses.teacher_id== get_teacher_id.first().id).order_by(models.Courses.id).all()
    query_object= db.query(models.CoursesTags).filter(models.CoursesTags.teacher_id== get_teacher_id.first().id).order_by(asc(models.CoursesTags.id)).all()
    # query_object= db.query(models.CoursesTags).join(models.Courses).options(joinedload(models.CoursesTags.courses)).order_by(asc(models.Courses.id)).all()

    #+++++ NOW PARSING THE OBJECT QUERY INSTANCE INTO RESPONSE PYDANTIC MODEL AND SETTING THE PREFERRED LINK INTO IT
    object_to_json_list= []
    for i in query_object:
        bucket_folder_path= f'teacher/courses/{i.id}/cover_picture'

        # object_to_json= schemas.CoursesTags.parse_obj(i)#TP MAKE THIS WORK, YOU WIL HAVE TO SET THE from orm TO TRUE IN THE SCHEMA MODEL CLASS CONFIG, SO THIS WILL THEN BE ABLE TO PARSE IN THE OBJECT
        object_to_json= schemas.CoursesTags(
            date= i.date,
            id= i.id,
            about= i.about,
            category= i.category,
            level= i.level,
            cover_picture= i.cover_picture,
            total_enrolled= i.total_enrolled,
            price= i.price,
            material_includes= i.material_includes,
            requirements= i.requirements,
            audience= i.audience,
            teacher_id= i.teacher_id,
            courses= courses_object,
            teacher_profile_tag= i.teacher_profile_tag,
            students= i.students,
            quiz_to_course= i.quiz_to_course
        )


        get_preferred_link= await s3Bucket.s3_get_presigned_link(bucket_folder_path, i.cover_picture)
        object_to_json.cover_picture = get_preferred_link


        for i2 in object_to_json.courses:
            # +++++++ FILE PICTURE +++++++
            bucket_folder_path= f'teacher/courses/{i.id}/file_picture'
            get_preferred_link= await s3Bucket.s3_get_presigned_link(bucket_folder_path, i2.cover_picture)
            # print(get_preferred_link)
            i2.cover_picture= get_preferred_link
            # +++++ VIDEO ++++++
            bucket_folder_path= f'teacher/courses/{i.id}/file_video'
            get_preferred_link= await s3Bucket.s3_get_presigned_link(bucket_folder_path, i2.video)
            i2.video= get_preferred_link
            # ++++++ PDF +++++++
            bucket_folder_path= f'teacher/courses/{i.id}/file_pdf'
            if i2.pdf:
                get_preferred_link= await s3Bucket.s3_get_presigned_link(bucket_folder_path, i2.pdf)
                i2.pdf= get_preferred_link

        object_to_json_list.append(object_to_json)
    return object_to_json_list
    # return db.query(models.CoursesTags).filter(models.CoursesTags.teacher_id== get_teacher_id.first().id).all()


async def view_by_tag(tag, db, username):
    get_teacher_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_teacher_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_teacher_id.first().role == "student":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_teacher_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_teacher_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Teacher with this username: '{username}' does not exist or has been removed")
    
    get_course= db.query(models.CoursesTags).filter(models.CoursesTags.teacher_id== get_teacher_id.first().id).filter(models.CoursesTags.id== tag).first()
    if not get_course:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"This course: '{tag}' does not exist or has been removed")
    return get_course


async def update(cover_picture, file_pictures, file_videos, file_pdfs, request, db, username):
    
    get_teacher_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_teacher_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_teacher_id.first().role == "student":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")
    
    if get_teacher_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_teacher_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Teacher with this username: '{username}' does not exist or has been removed")
    

    courses= db.query(models.CoursesTags).filter(models.CoursesTags.id== request.id)
    if not courses.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Course with this tag: '{request.id}' does not exist or has been removed")
    if courses.first().teacher_id != get_teacher_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Course with this id: '{request.id}' could not be matched with any of your course")




    # ++++++ COVER PICTURE FILE +++++++++
    if cover_picture != None:
        # get_clean_file_name= f"{os.path.splitext(courses.first().cover_picture)[0].split('/')[-1]}.jpg"
        bucket_folder_path= f'teacher/courses/{request.id.title()}/cover_picture'
        get_url= await s3Bucket.s3_upload_replacement(cover_picture, courses.first().cover_picture, bucket_folder_path, True)
        # courses.update({'cover_picture': f'{get_url}'})
        # db.commit()
        #

    # ++++++ FILE PICTURES +++++++++
    if file_pictures != None:
        for i in file_pictures:
            get_file_picture= db.query(models.Courses).filter(models.Courses.id == int (os.path.splitext(i.filename)[0]))
            if get_file_picture.first().cover_picture:
                bucket_folder_path= f'teacher/courses/{request.id.title()}/file_picture'
                get_url= await s3Bucket.s3_upload_replacement(i, get_file_picture.first().cover_picture, bucket_folder_path, True)
                # get_file_picture.update({'cover_picture': f'{get_url}'})
                # db.commit()
                

    # ++++++ FILE VIDEOS +++++++++
    if file_videos != None:
        for i in file_videos:
            get_file_video= db.query(models.Courses).filter(models.Courses.id == int (os.path.splitext(i.filename)[0]))
            if get_file_video.first().video:
                bucket_folder_path= f'teacher/courses/{request.id.title()}/file_video'
                get_url= await s3Bucket.s3_upload_replacement(i, get_file_video.first().video, bucket_folder_path, False)
                # get_file_video.update({'video': f'{get_url}'})
                # db.commit()
    

    # ++++++++ FILE PDF +++++++++++
    if file_pdfs != None:
        for i in file_pdfs:
            get_file_pdf= db.query(models.Courses).filter(models.Courses.id == int (os.path.splitext(i.filename)[0]))
            if get_file_pdf.first().pdf:
                bucket_folder_path= f'teacher/courses/{request.id.title()}/file_pdf'
                get_url= await s3Bucket.s3_upload_replacement(i, get_file_pdf.first().pdf, bucket_folder_path, False)
                # get_file_pdf.update({'pdf': f'{get_url}'})
                # db.commit()
            
            else:
                bucket_folder_path= f'teacher/courses/{request.id.title()}/file_pdf'
                get_url= await s3Bucket.s3_upload(i, bucket_folder_path, False)
                get_file_pdf.update({'pdf': f'{get_url}'})
                db.commit()


    #+++++++ FILTERING OUT THE NONE FIELDS
    new_course= {}
    for i in request:
        if i[0] != "sub_courses" and i[1] is not None and i[1] != []:
            new_course.setdefault(i[0], i[1])
    if new_course != {}:
        courses.update(new_course)
        db.commit()


    if request.sub_courses != [] and request.sub_courses != None:
        for i in request.sub_courses:
            new_sub_course= {}
            get_course_id_loop= None
            for i2 in i:
                if i2[1] is not None:
                    new_sub_course.setdefault(i2[0], i2[1])
            
            courses= db.query(models.Courses).filter(models.Courses.id== int(new_sub_course['id']))
            if not courses.first():
                raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Course with this id: '{new_sub_course['id']}' does not exist or has been removed")
            if courses.first().teacher_id != get_teacher_id.first().id:
                raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Course with this id: '{new_sub_course['id']}' could not be matched with any of your course")
            
            new_sub_course['title']= new_sub_course['title'].title()
            courses.update(new_sub_course)
            db.commit()




async def delete(course_id, db, username):
    get_teacher_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_teacher_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_teacher_id.first().role == "student":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")
    
    if get_teacher_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_teacher_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Teacher with this username: '{username}' does not exist or has been removed")
    
    courses= db.query(models.Courses).filter(models.Courses.id== int(course_id))
    if not courses.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Course with this id: '{course_id}' does not exist or has been removed")
    if courses.first().teacher_id != get_teacher_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Course with this id: '{course_id}' could not be matched with any of your course")


    courses.delete(synchronize_session= False)
    db.commit()



async def delete_by_tag(tag, db, username):
    get_teacher_id= db.query(models.Users).filter(models.Users.username==username)
    if not get_teacher_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_teacher_id.first().role == "student":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")
    
    if get_teacher_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_teacher_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Teacher with this username: '{username}' does not exist or has been removed")
    
    courses= db.query(models.CoursesTags).filter(models.CoursesTags.id== tag)
    if not courses.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Course with this tag: '{tag}' does not exist or has been removed")
    if courses.first().teacher_id != get_teacher_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Course with this tag: '{tag}' could not be matched with any of your course")

    
    sub_courses= db.query(models.Courses).filter(models.Courses.tags== tag)
    if not sub_courses.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Sub Course with this id: '{tag}' does not exist or has been removed")
    if sub_courses.first().teacher_id != get_teacher_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Sub Course with this id: '{tag}' could not be matched with any of your course")


            

    # ++++++ FILE PICTURES +++++++++
    for i in sub_courses:
        delete_picture= False
        delete_video= False
        delete_pdf= False

        #++++++ FIEL PDFS +++++++
        if i.cover_picture != None:
            bucket_folder_path= f'teacher/courses/{tag}/file_picture'
            get_delete= await s3Bucket.s3_delete(i.cover_picture, bucket_folder_path)
            if get_delete:
                delete_picture= True
        else: #+++++ IN CASE IT HAS ALREADY BEING DELETED AND OTHER FILES LIKE VIDEO HAS NOT
            delete_picture= True
  

        # ++++++ FILE VIDEOS +++++++++
        if i.video != None:
            bucket_folder_path= f'teacher/courses/{tag}/file_video'
            get_delete= await s3Bucket.s3_delete(i.video, bucket_folder_path)
            if get_delete:
                delete_video= True
        else:
            delete_video= True
    

        # ++++++++ FILE PDF +++++++++++
        if i.pdf != None:
            bucket_folder_path= f'teacher/courses/{tag}/file_pdf'
            get_delete= await s3Bucket.s3_delete(i.pdf, bucket_folder_path)
            if get_delete:
                delete_pdf= True
        else:
            delete_pdf= True
        
        if delete_picture== True and delete_video== True and delete_pdf== True:
            course_instance= db.query(models.Courses).filter(models.Courses.id== i.id)
            course_instance.delete(synchronize_session= False)
            db.commit()
        else:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Something went wrong, we could not fully carry out your request")


    # ++++++ COVER PICTURE FILE +++++++++
    # get_clean_file_name= f"{os.path.splitext(courses.first().cover_picture)[0].split('/')[-1]}.jpg"
    bucket_folder_path= f'teacher/courses/{tag}/cover_picture'
    get_delete= await s3Bucket.s3_delete(courses.first().cover_picture, bucket_folder_path)
    if get_delete:
        courses.delete(synchronize_session= False)
        db.commit()


    
    course_no= 0
    get_total_course_no= db.query(models.Total_Teacher_Everything).filter(models.Total_Teacher_Everything.teachers_id == get_teacher_id.first().id)
    if get_total_course_no.first():
        course_no= get_total_course_no.first().total_course_no
        total_everything_no= {
            "total_course_no" :  course_no - 1
        }

        get_total_course_no.update(total_everything_no)
        db.commit()





#Teacher adding quiz
async def add_quiz(request, db, username):
    get_teacher_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_teacher_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_teacher_id.first().role == "student":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")
    
    if get_teacher_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_teacher_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Teacher with this username: '{username}' does not exist or has been removed")
    
    courses= db.query(models.Courses).filter(models.Courses.tags== request.tag)
    if not courses.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Course with this tag: '{request.tag}' does not exist or has been removed")
    if courses.first().teacher_id != get_teacher_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Course with this tag: '{request.tag}' could not be matched with any of your course")
    

    if not db.query(models.CoursesTags).filter(models.CoursesTags.id== request.tag).first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "This course is no longer available")
    
    if db.query(models.QuizUmbrella).filter(models.QuizUmbrella.id == request.tag).first():
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail= "A quiz has already been formed for this course")
    quiz_umbrella= models.QuizUmbrella(id= request.tag, quiz_duration= request.duration, difficulty= db.query(models.CoursesTags).filter(models.CoursesTags.id== request.tag).first().level, course_id= request.tag)
    db.add(quiz_umbrella)
    db.commit()

    for i in request.quiz:
        quiz_model= models.Quiz(tag= request.tag, question=i.question, answer= i.answer, teachers_id= get_teacher_id.first().id, quiz_umbrella_id= quiz_umbrella.id)
        db.add(quiz_model)
        db.commit()
        
        for i2 in range (4):
            quiz_option= models.QuizOptions(question_options_id= quiz_model.id, option= i.options[i2])
            db.add(quiz_option)
            db.commit()

    db.refresh(quiz_umbrella), db.refresh(quiz_model), db.refresh(quiz_option)
    



async def view_quiz(db, username):
    get_teacher_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_teacher_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_teacher_id.first().role == "student":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_teacher_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_teacher_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"User with this username: '{username}' does not exist or has been removed")
    
    if get_teacher_id.first().role == "admin":
        return db.query(models.QuizUmbrella).all()
    
    #return models.QuizUmbrella.quiz.contains(models.Quiz)
    return db.query(models.QuizUmbrella).all()



async def view_quiz_by_tag(tag, db, username):
    get_teacher_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_teacher_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_teacher_id.first().role == "student":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_teacher_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_teacher_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"User with this username: '{username}' does not exist or has been removed")
    
    if get_teacher_id.first().role == "admin":
        return db.query(models.Quiz).filter(models.Quiz.tag== tag).all()
    verify_first= db.query(models.Quiz).filter(models.Quiz.teachers_id== get_teacher_id.first().id).filter(models.Quiz.tag== tag)
    if verify_first.first():
        return db.query(models.QuizUmbrella).filter(models.QuizUmbrella.id == tag).first()
    
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f'The quiz with this tag {tag} no longer exist')



async def remove_quiz(tag, options_id, db, username):
    get_teacher_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_teacher_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_teacher_id.first().role == "student":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this operation")
    
    if get_teacher_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_teacher_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Teacher with this username: '{username}' does not exist or has been removed")
    

    
    for i in range (len(options_id)):
        quiz_option= db.query(models.QuizOptions).filter(models.QuizOptions.question_options_id== int(options_id[i].question_options_id))
        quiz_option.delete(synchronize_session= False)
        db.commit()

 
    quiz= db.query(models.Quiz).filter(models.Quiz.tag== tag)

    quiz_umbrella= db.query(models.QuizUmbrella).filter(models.QuizUmbrella.id== tag)
    if not quiz_umbrella.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Quiz with this id: '{tag}' does not exist or has been removed")
    
    quiz.delete(synchronize_session= False)
    db.commit()

    quiz_umbrella.delete(synchronize_session= False)
    db.commit()




async def view_total_everything(db, username):
    get_teacher_id= db.query(models.Users).filter(models.Users.username==username)

    if not get_teacher_id.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Your account has been removed")
    
    if get_teacher_id.first().role == "student":
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this content")
    
    if get_teacher_id.first().activated == "false":
        raise HTTPException(status_code= status.HTTP_401_sUNAUTHORIZED, detail="Your account was deactivated, please send us mail in the contact centre to access your account")
    
    if not get_teacher_id.first().id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"User with this username: '{username}' does not exist or has been removed")
    

    if not db.query(models.Total_Teacher_Everything).filter(models.Total_Teacher_Everything.teachers_id== get_teacher_id.first().id).first():
        create_anyway= models.Total_Teacher_Everything(teachers_id= get_teacher_id.first().id)
        db.add(create_anyway)
        db.commit()
        db.refresh(create_anyway)
    
    
    teacher_everything= db.query(models.Total_Teacher_Everything).filter(models.Total_Teacher_Everything.teachers_id== get_teacher_id.first().id).first()
    
    #+++++ NOW PARSING THE OBJECT QUERY INSTANCE INTO RESPONSE PYDANTIC MODEL AND SETTING THE PREFERRED LINK INTO IT
    object_to_json= schemas.TotalTeacherEverything.parse_obj(teacher_everything)#TP MAKE THIS WORK, YOU WIL HAVE TO SET THE from orm TO TRUE IN THE SCHEMA MODEL CLASS CONFIG, SO THIS WILL THEN BE ABLE TO PARSE IN THE OBJECT
    
        # +++++++ PARSING OBJECTS TO RESTRUCTURE THE RESPONSE MODEL BY SUBSTITUTING A PREFFERED LINK FROM S3 BUCKET FOR THE NAME OF THE FILE STORE IN THE DB 
    bucket_folder_path= f'teacher/profile_picture/{teacher_everything.teachers_id}'
    if teacher_everything.teachers.profile_picture:
        get_preferred_link= await s3Bucket.s3_get_presigned_link(bucket_folder_path,teacher_everything.teachers.profile_picture)
        object_to_json.teachers.profile_picture = get_preferred_link

    return object_to_json
    # return schemas.TotalTeacherEverything. model_dump(db.query(models.Total_Teacher_Everything).filter(models.Total_Teacher_Everything.teachers_id== get_teacher_id.first().id).first())
    # return db.query(models.Total_Teacher_Everything).filter(models.Total_Teacher_Everything.teachers_id== get_teacher_id.first().id).first()

