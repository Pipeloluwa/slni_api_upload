from pydantic import BaseModel, Field
from typing import List, Optional
from pydantic.types import constr



#The reason why some base model relationship key variables of a class require to be wrapped in a List form to prevent validation error is because the foreign unique key for linking to
# two relationships of classes together is not residing in that class, hence, one has to put it inside a List

class SignUp(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: str
    password: str
    password_confirmation: str

class Info(BaseModel):
    username: constr(to_lower= True)
    email: str

    class Config():
        from_attributes= True

class Base(Info):
    password: str
    class Config():
        from_attributes= True

class PhoneNo(BaseModel):
    phone_no: str

class Otp(BaseModel):
    phone_or_email: str
    otp_token: str

class SendMailOnly(BaseModel):
    Subject: str
    Body: str
    To: str
    Cc: Optional[str]= None
    Bcc: Optional[str]= None

class SendMail(BaseModel):
    Subject: str
    To: str
    Cc: Optional[str]= None
    Bcc: Optional[str]= None
    Filename: Optional[str]= None
    class Config():
        from_attributes= True

class StudentsUser(BaseModel):
    id: int
    activated: str
    username: str
    email: str
    # courses: str
    # review: str
    # quiz: str
    # payment: str
    registration_date: str
    class Config():
        from_attributes= True

class ViewProfile(BaseModel):
    users_id: int
    activated: str
    registration_date: str
    firstname: Optional[str]
    lastname: Optional[str]
    username: str
    email: str
    phone_no: Optional[str]
    skill_occupation: Optional[str]
    biography: Optional[str]
    profile_picture: Optional[str]
    
    #students: StudentsUser
    class Config():
        from_attributes= True

class ViewProfileStudents(BaseModel):
    profile: List[ViewProfile]= []
    class Config():
        from_attributes= True


class UsersProfile(BaseModel):
    firstname: Optional[constr(to_lower= True)]= None
    lastname: Optional[constr(to_lower= True)]= None
    email: Optional[constr(to_lower= True)]= None
    phone_no: Optional[str]= None
    skill_occupation: Optional[str]= None
    biography: Optional[str]= None
    profile_picture: Optional[str]= None
    class Config():
        from_attributes= True

class UsersProfileForm(BaseModel):
    firstname: Optional[constr(to_lower= True)]= None
    lastname: Optional[constr(to_lower= True)]= None
    email: Optional[constr(to_lower= True)]= None
    phone_no: Optional[str]= None
    skill_occupation: Optional[str]= None
    biography: Optional[str]= None
    class Config():
        from_attributes= True

class ToggleStudents_Activation(BaseModel):
    activated: str

class StudentsLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str



class CourseRegister(BaseModel):
    title: str
    # cover_picture: Optional[str]= None
    # video: Optional[str]= None
    # pdf: Optional[str]= None
    # tags: Optional[str]= None


class CourseAllRegister(BaseModel):
    id: str
    about: Optional[str]= None
    category: Optional[str]= None
    level: Optional[str]= None
    price: Optional[str]= None
    material_includes: Optional[str]= None
    requirements: Optional[str]= None
    audience: Optional[str]= None
    sub_courses: List[CourseRegister]


class CourseIDUpdate(BaseModel):
    id: str
    title: Optional[str]= None
    # cover_picture: Optional[str]= None
    # video: Optional[str]= None
    # pdf: Optional[str]= None
    class Config():
        from_attributes= True

class CourseAllUpdate(BaseModel):
    id: str
    about: Optional[str]= None
    category: Optional[str]= None
    level: Optional[str]= None
    cover_picture: Optional[str]= None
    price: Optional[str]= None
    material_includes: Optional[str]= None
    requirements: Optional[str]= None
    audience: Optional[str]= None
    sub_courses: Optional[List[CourseIDUpdate]]= None
    class Config():
        from_attributes= True



class Course(BaseModel):
    date: str
    id: int
    title: str
    cover_picture: Optional[str]= None
    video: str
    pdf: Optional[str]= None
    tags: Optional[str]= None
    teacher_id: int

    # @property
    # def sorted_by_id(self):
    #     return sorted(self.dict(), key=lambda x: x["id"])
    class Config():
        from_attributes= True
    

    # def __str__(self):
    #     return (
    #                 f"Course(id={self.id}, title='{self.title}', date='{self.date}', "
    #                 f"cover_picture={self.cover_picture}, video='{self.video}', "
    #                 f"pdf={self.pdf}, tags={self.tags}, teacher_id={self.teacher_id})"
    #             )
        




class CourseTeacher(BaseModel):
    date: str
    id: int
    title: str
    about: Optional[str]= None
    category: Optional[str]= None
    level: Optional[str]= None
    cover_picture: Optional[str]= None
    total_enrolled: Optional[str]= None
    video: str
    pdf: Optional[str]= None
    price: Optional[str]= None
    material_includes: Optional[str]= None
    requirements: Optional[str]= None
    tags: Optional[str]= None
    audience: Optional[str]= None
    teacher_id: int
    teacher_profile: ViewProfile
    class Config():
        from_attributes= True



class CourseStudentModel(BaseModel):
    id: int
    registration_date: str
    course_tag: str
    student_review: Optional[str]= None
    students_id: int
    students_profile: ViewProfile
    has_paid: str
    class Config():
        from_attributes= True



class QuizForm(BaseModel):
    question: str
    answer: str
    options: List
    class Config():
        from_attributes= True

class Quiz(BaseModel):
    tag: str
    duration: int
    quiz: List[QuizForm]
    class Config():
        from_attributes= True
    

class QuizOption(BaseModel):
    question_options_id: int
    option: str
    class Config():
        from_attributes= True

class QuizAnswer(BaseModel):
    question_id: int
    tag: str
    student_answer: str
    class Config():
        from_attributes= True

class QuizStudents(BaseModel):
    id: int
    date: str
    tag: str
    student_answer: str
    result: str
    students_id: int
    students: ViewProfile
    class Config():
        from_attributes= True
    

class QuizView(BaseModel):
    id: int
    date: str
    tag: str
    question: str
    answer: str

    quiz_options: List[QuizOption]= []
    quiz_umbrella_id: str
    teachers_id: int
    teachers: ViewProfile
    students: List[QuizStudents]= []
    class Config():
        from_attributes= True


class CoursesTagsBase(BaseModel):
    date: str
    id: str
    about: Optional[str]= None
    category: Optional[str]= None
    level: Optional[str]= None
    cover_picture: Optional[str]= None
    total_enrolled: Optional[str]= None
    price: Optional[str]= None
    material_includes: Optional[str]= None
    requirements: Optional[str]= None
    audience: Optional[str]= None
    teacher_id: int
    courses: List[Course]
    teacher_profile_tag: ViewProfile
    students: List[CourseStudentModel]

    class Config():
        from_attributes= True
        # arbitrary_types_allowed= True

        # Specify the alias to order the courses based on their ID
        # @staticmethod
        # def json_schema_extra(schema, model):
        #     print(schema)
            # schema['properties']['courses']['items']['properties']['id']['default']= 0
            # schema['properties']['courses']['items']['sorted_by'] = 'id'


    # # Custom property to sort courses by their ID
    # @property
    # def order_sort_courses(self):
    #     return sorted(self.courses,key= lambda course : course.id)

    # # Custom property to sort courses by their ID
    # @property
    # def order_sort_courses(self):
    #     return sorted(self.courses,key= lambda course : course.id)


class QuizUmbrella(BaseModel):
    id: str
    quiz_duration: int
    difficulty: str
    date: str
    quiz: List[QuizView] = []
    course_id: str
    course: CoursesTagsBase
    class Config():
        from_attributes= True


class CoursesTags(CoursesTagsBase):
    quiz_to_course: List[QuizUmbrella]= None
    class Config():
        from_attributes= True


class CourseStudent(CourseStudentModel):
    course: CoursesTags


class AllCourseInfo(BaseModel):
    date: str
    id: int
    title: str
    video: str
    pdf: str
    tags: str
    teacher_id: int
    teacher_profile: ViewProfile
    students: List[CourseStudent]= []
    class Config():
        from_attributes= True


class QuizViewByTag(BaseModel):
    quiz_umbrella_relationship: QuizUmbrella


class QuizOptionID(BaseModel):
    question_options_id: int

class QuizViewStudents(BaseModel):
    quiz: QuizView

class QuizTotalResult(BaseModel):
    tag: str
    level: str
    students_id: int

class ViewQuizTotalResult(BaseModel):
    id: int
    date: str
    tag: str
    level: str
    result: str
    students_id: int
    students: ViewProfile
    class Config():
        from_attributes= True


class TotalTeacherEverything(BaseModel):
    id: int
    date: str
    total_course_no: int
    total_enrolled_no: int
    total_quiz_taken: int
    teachers_id: int
    teachers: ViewProfile
    class Config():
        from_attributes= True

    
class Total_Students_Everything(BaseModel):
    id: int
    date: str
    total_enrolled_no: int
    total_quiz_taken: int
    student_level_rating: int
    obtainable_level_rating: int
    students_id: int
    students: ViewProfile
    class Config():
        from_attributes= True


# class QuizStudentsView(BaseModel):
#     date: str
#     student_answer: str
#     students_id: int
#     quiz_id: int
#     quiz: List[QuizView]= []



class Review(BaseModel):
    review: str


class TokenDataUser(BaseModel):
    username: Optional[str]= None

class Sample(BaseModel):
    To: str
