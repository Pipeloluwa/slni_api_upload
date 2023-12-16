from fastapi import APIRouter, Depends, status, Response, HTTPException, UploadFile, File
from ..models import EmailContents
from typing import Optional, List, Annotated
from .. import schemas, database, models, oauth2
from ..repositories import s3Bucket
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from twilio.rest import Client
import random
import smtplib
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
from pathlib import Path
from ..repositories import html_token_template
import uuid


load_dotenv()

router= APIRouter(prefix="/otp-management", tags= ["OTP MANAGEMENT"])
get_db= database.get_database

HOST= os.getenv("HOST")
PORT: int= os.getenv("PORT")
HOST_CLIENT_EMAIL= os.getenv("HOST_CLIENT_EMAIL")
HOST_CLIENT_PASSWORD= os.getenv("HOST_CLIENT_PASSWORD")
CLIENT_EMAIL= "pipeloluwa14@gmail.com"

BASE_DIR = Path(__file__).resolve().parent.parent
FILE_DIR= f"{BASE_DIR}/template"
CONTENT= f"{BASE_DIR}/contents"

async def start_conn():
    smtp= smtplib.SMTP(HOST, PORT)
    smtp.starttls()
    smtp.login(HOST_CLIENT_EMAIL, HOST_CLIENT_PASSWORD)
    return smtp


@router.get("/send-mail-content_token")
async def send_mail_content_token():
    smtp= await start_conn()
    MESSAGE= MIMEMultipart("alternative")
    MESSAGE['Subject']= "Mail Sent from Papic"
    MESSAGE['From']= HOST_CLIENT_EMAIL
    MESSAGE['To']= CLIENT_EMAIL
    MESSAGE['Cc']= HOST_CLIENT_EMAIL
    MESSAGE['Bcc']= HOST_CLIENT_EMAIL
    
    n= str (random.randint(100000, 999999))
    st_html=  await html_token_template.HtmlTemplate.insert_token(n)

    html_part= MIMEText(st_html, "html")
    MESSAGE.attach(html_part)
    
    smtp.sendmail(HOST_CLIENT_EMAIL, CLIENT_EMAIL, MESSAGE.as_string())
    smtp.quit()


@router.post("/send-mail-text-only")
async def send_mail_text_only(request: schemas.SendMailOnly, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    if not db.query(models.Admin).filter(models.Admin.username==current_user.username).first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)

    smtp= await start_conn()

    if not request.Cc and not request.Bcc:
        MESSAGE= MIMEMultipart("alternative")
        MESSAGE['Subject']= request.Subject
        MESSAGE['From']= HOST_CLIENT_EMAIL
        MESSAGE['To']= request.To

    elif not request.Bcc:
        MESSAGE= MIMEMultipart("alternative")
        MESSAGE['Subject']= request.Subject
        MESSAGE['From']= HOST_CLIENT_EMAIL
        MESSAGE['To']= request.To
        MESSAGE['Cc']= request.Cc

    else:
        MESSAGE= MIMEMultipart("alternative")
        MESSAGE['Subject']= request.Subject
        MESSAGE['From']= HOST_CLIENT_EMAIL
        MESSAGE['To']= request.To
        MESSAGE['Cc']= request.Cc
        MESSAGE['Bcc']= request.Bcc
    
    part= MIMEText(request.Body, "html")
    MESSAGE.attach(part)
    smtp.sendmail(HOST_CLIENT_EMAIL, request.To, MESSAGE.as_string())
    smtp.quit()


# @router.post("/send-content")
# async def send_content(file: UploadFile, db: Session= Depends(get_db)):
#     file_ext= mimetypes.guess_type(file.filename)[0].split("/")[1]
#     file.filename= f"{uuid.uuid4()}.{file_ext}"
#     file_path_name= f"{CONTENT}/{file.filename}"
#     contents= await file.read()
#     with open(f"{file_path_name}", "wb") as f:
#         f.write(contents)
#     save_mail= models.EmailContents(filename= file_path_name)
#     db.add(save_mail)
#     db.commit()
#     db.refresh(save_mail)
#     return {"filename": file_path_name}

@router.post("/send-mail-with-content")
async def send_mail_with_content(request: schemas.SendMail, filepath: UploadFile, db: Session= Depends(get_db), current_user: schemas.StudentsLogin= Depends(oauth2.get_current_user)):
    if not db.query(models.Admin).filter(models.Admin.username==current_user.username).first():
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)

    smtp= await start_conn()
    MESSAGE= MIMEMultipart("alternative")
    MESSAGE['Subject']= request.Subject
    MESSAGE['From']= HOST_CLIENT_EMAIL
    MESSAGE['To']= request.To
    MESSAGE['Cc']= request.Cc
    MESSAGE['Bcc']= request.Bcc
    
    filepath= db.query(models.EmailContents).filter(models.EmailContents.filename== request.Filename).first()
    if not filepath:
        raise HTTPException(status_code= status.HTTP_204_NO_CONTENT, detail= "Please try and send the mail again, we could not retrieve your attached file")
    filepath= filepath.filename
    content= ""
    file_obj= None
    with open(filepath, "rb") as f:
        content= f.read()
        file_obj= f

    check_file_category= mimetypes.guess_type(file_obj.name)[0].split("/")[0]
    get_file_type= mimetypes.guess_type(file_obj.name)[0].split("/")[1]

    if check_file_category == "text":
        content= content.decode()
            
    part= MIMEText(content, get_file_type)
    MESSAGE.attach(part)
    
    if check_file_category== "text":
        smtp.sendmail(HOST_CLIENT_EMAIL, request.To, MESSAGE.as_string())
    if not check_file_category== "text":
        smtp.sendmail(HOST_CLIENT_EMAIL, request.To, MESSAGE)
    smtp.quit()

