from sqlalchemy import Column, Integer, String, ForeignKey
from .database import Base
from sqlalchemy.orm import relationship
import time

class Admin(Base):
    __tablename__= "admin"
    id= Column(Integer, primary_key=True, index= True)
    username= Column(String, unique=True)
    role= Column(String)
    email= Column(String, unique=True)
    registration_date= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))
    user_id= Column(Integer, ForeignKey('users.id'))
    user= relationship("Users", back_populates="admin")


class Users(Base):
    __tablename__= "users"
    activated= Column(String, default= True)
    id= Column(Integer, primary_key=True, index= True)
    username= Column(String, unique=True)
    role= Column(String)
    email= Column(String, unique=True)
    password= Column(String)
    profile= relationship("Profile", back_populates="users")
    registration_date= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))

    admin= relationship("Admin", back_populates="user")


class Profile(Base):
    __tablename__= "profile"
    id= Column(Integer, primary_key=True, index= True)
    activated= Column(String, default= True)
    registration_date= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))
    firstname= Column(String)
    lastname= Column(String)
    username= Column(String, unique=True)
    email= Column(String, unique=True)
    phone_no= Column(String)
    skill_occupation= Column(String)
    biography= Column(String)
    role= Column(String)
    profile_picture= Column(String)

    users_id= Column(Integer, ForeignKey('users.id'))
    users= relationship("Users", back_populates="profile")
    teacher_courses= relationship("Courses", back_populates="teacher_profile")
    students_courses= relationship("StudentsCourse", back_populates="students_profile")
    teachers_quiz= relationship("Quiz", back_populates="teachers")
    students_quiz= relationship("QuizStudents", back_populates="students")
    students_total_result= relationship("QuizResult", back_populates="students")
    teacher_courses_tags= relationship("CoursesTags", back_populates="teacher_profile_tag")
    tt_everything= relationship("Total_Teacher_Everything", back_populates="teachers")
    st_everything= relationship("Total_Students_Everything", back_populates="students")


class Courses(Base):
    __tablename__= "courses"
    date= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))
    id= Column(Integer, primary_key=True, index= True)
    title= Column(String)
    cover_picture= Column(String)
    video= Column(String)
    pdf= Column(String)

    tags= Column(String, ForeignKey('tags.id'))
    course_tags= relationship("CoursesTags", back_populates="courses")
    teacher_id= Column(Integer, ForeignKey('profile.id'))
    teacher_profile= relationship("Profile", back_populates="teacher_courses")


class CoursesTags(Base):
    __tablename__= "tags"
    date= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))
    id= Column(String, primary_key=True, index= True, unique= True)

    about= Column(String)
    category= Column(String)
    level= Column(String)
    total_enrolled= Column(String, default=0)
    cover_picture= Column(String)
    price= Column(String)
    material_includes= Column(String)
    requirements= Column(String)
    audience= Column(String)

    teacher_id= Column(Integer, ForeignKey('profile.id'))
    teacher_profile_tag= relationship("Profile", back_populates="teacher_courses_tags")

    courses= relationship("Courses", back_populates="course_tags")
    students= relationship("StudentsCourse", back_populates="course")
    quiz_to_course= relationship("QuizUmbrella", back_populates= "course")
    

class StudentsCourse(Base):
    __tablename__= "studentscourse"
    id= Column(Integer, primary_key=True, index= True)
    registration_date= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))

    student_review= Column(String)
    students_id= Column(Integer, ForeignKey('profile.id'))
    students_profile= relationship("Profile", back_populates="students_courses")

    course_tag= Column(String, ForeignKey('tags.id'))
    course= relationship("CoursesTags", back_populates="students")

    has_paid= Column(String)




class QuizUmbrella(Base):
    __tablename__= "quiz_umbrella"
    id= Column(String, primary_key=True, index=True)
    quiz_duration= Column(Integer)
    difficulty= Column(String)
    date= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))
    quiz= relationship("Quiz", back_populates="quiz_umbrella_relationship")
    course_id= Column(String, ForeignKey('tags.id'))
    course= relationship("CoursesTags", back_populates= "quiz_to_course")



class Quiz(Base):
    __tablename__= "quiz"
    id= Column(Integer, primary_key=True, index= True)
    tag= Column(String)
    date= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))
    question= Column(String)
    answer= Column(String)
    
    
    quiz_options= relationship("QuizOptions", back_populates="options")
    teachers_id= Column(Integer, ForeignKey('profile.id'))
    teachers= relationship("Profile", back_populates="teachers_quiz")
    students= relationship("QuizStudents", back_populates="quiz")

    quiz_umbrella_id= Column(String, ForeignKey('quiz_umbrella.id'))
    quiz_umbrella_relationship= relationship("QuizUmbrella", back_populates="quiz")
    

class QuizOptions(Base):
    __tablename__= "options_of_quiz"
    id= Column(Integer, primary_key=True, index= True)
    option= Column(String)

    question_options_id= Column(Integer, ForeignKey('quiz.id'))
    options= relationship("Quiz", back_populates="quiz_options")


class QuizStudents(Base):
    __tablename__= "quiz_students"
    id= Column(Integer, primary_key=True, index= True)
    date= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))
    tag= Column(String)
    student_answer= Column(String)
    result= Column(String)

    students_id= Column(Integer, ForeignKey('profile.id'))
    students= relationship("Profile", back_populates="students_quiz")
    quiz_id= Column(Integer, ForeignKey('quiz.id'))
    quiz= relationship("Quiz", back_populates="students")


class QuizResult(Base):
    __tablename__= "quiz_result"
    id= Column(Integer, primary_key=True, index=True)
    date= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))
    tag= Column(String)
    level= Column(String)
    students_id= Column(Integer, ForeignKey('profile.id'))
    students= relationship("Profile", back_populates="students_total_result")
    result= Column(String)



class Total_Teacher_Everything(Base):
    __tablename__= "total_teacher_everything"
    id= Column(Integer, primary_key=True, index=True)
    date= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))
    total_course_no= Column(Integer, default= 0)
    total_enrolled_no= Column(Integer, default= 0)
    total_quiz_taken= Column(Integer, default= 0)
    teachers_id= Column(Integer, ForeignKey('profile.id'))
    teachers= relationship("Profile", back_populates="tt_everything")


class Total_Students_Everything(Base):
    __tablename__= "total_students_everything"
    id= Column(Integer, primary_key=True, index=True)
    date= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))
    total_enrolled_no= Column(Integer, default= 0)
    total_quiz_taken= Column(Integer, default= 0)
    student_level_rating= Column(Integer, default=0)
    obtainable_level_rating= Column(Integer, default=0)
    students_id= Column(Integer, ForeignKey('profile.id'))
    students= relationship("Profile", back_populates="st_everything")



# class TeachersUser(Base):
#     __tablename__= "teachers"
#     id= Column(Integer, primary_key=True, index= True)

#     courses= relationship("Courses", back_populates="teachers")
#     user_id= Column(Integer, ForeignKey('users.id'))



# class Payment(Base):
#     __tablename__= "withdrawal"
#     id= Column(Integer, primary_key=True, index= True)
#     date= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))
#     amount= Column(String)
#     ref= Column(String)
    
#     course_id= Column(Integer, ForeignKey('courses.id'))
#     courses= relationship("Courses", back_populates="payment")
#     students_id= Column(Integer, ForeignKey('users.id'))
#     students= relationship("Users", back_populates="payment")

# class Review(Base):
#     __tablename__= "review"
#     id= Column(Integer, primary_key=True, index= True)
#     review= Column(String)

#     students_id= Column(Integer, ForeignKey('users.id'))
#     students= relationship("Users", back_populates="review")
#     date= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))



# class WithdrawalRecords(Base):
#     __tablename__= "withdrawalrecords"
#     date= Column(String, default= time.strftime("%Y%m%d-%H%M%S"))
#     amount= Column(String)

#     teachers_id= Column(Integer, ForeignKey('teachers.id'))
#     teachers= relationship("TeachersUser", back_populates="withdrawal")

class OtpSafe(Base):
    __tablename__= "Otps"
    id= Column(Integer, primary_key=True, index= True)
    phone_or_email= Column(String)
    otp_token= Column(String)

class EmailContents(Base):
    __tablename__= "Email_Contents"
    id= Column(Integer,primary_key=True, index=True)
    filename= Column(String)
