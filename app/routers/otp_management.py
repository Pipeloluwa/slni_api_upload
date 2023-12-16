from fastapi import APIRouter, Depends, status, Response, HTTPException
from .. import schemas, database, models
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from twilio.rest import Client
import random
import time

load_dotenv()

router= APIRouter(prefix="/otp-management", tags= ["OTP MANAGEMENT"])
get_db= database.get_database

account_sid = os.getenv("account_sid")
auth_token = os.getenv("auth_token")
phone_no= os.getenv("phone_no")



async def generate_token(db):
    n= str (random.randint(100000, 999999))
    check= db.query(models.OtpSafe).filter(models.OtpSafe.otp_token== n)
    try:
        if check.first():
            await generate_token(db)
    except:
        raise HTTPException(status_code= status.HTTP_503_SERVICE_UNAVAILABLE, detail= "All our tokens are used up, please try again later")
    return n

async def redress_number(no):
    if len(no) == 11:
        no= (no[1:])
    no= f"+234{no}"
    return no

@router.post("/send-phone-otp", status_code= status.HTTP_200_OK)
async def Send_Phone_OTP(request: schemas.PhoneNo, db: Session= Depends(get_db)):
    client_me = Client(account_sid, auth_token)
    client_phone_no= await redress_number(request.phone_no)
    n= await generate_token(db)
    otp_token= models.OtpSafe(otp_token= n)
    db.add(otp_token)
    db.commit()
    db.refresh(otp_token)
    
    try:
        client_me.messages.create(
            from_= phone_no,
            body=f'OTP: {n}',
            to= client_phone_no
            )
        return Response(content= f"OTP sent to: {client_phone_no}")
    except:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Something is wrong, or maybe check your phone number without adding your country code")
        

@router.post("/verify-phone-otp", status_code= status.HTTP_200_OK)
async def Verify_Phone_OTP(request: schemas.Otp, db: Session= Depends(get_db)):
    verify_= db.query(models.OtpSafe).filter(models.OtpSafe.phone_or_email== request.phone_or_email).filter(models.OtpSafe.otp_token== request.otp_token)
    if not verify_.first():
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Incorrect OTP or the OTP was already used up")
    
    verify_.delete(synchronize_session=False)
    db.commit()
    return Response(status_code= status.HTTP_200_OK, content= "Phone Number Verified Successfully")
        
