from fastapi import APIRouter, Depends, Query, Form, Request, status, Response, HTTPException, UploadFile, File
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
import requests
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

load_dotenv()

router= APIRouter(prefix="/payment-website", tags= ["Payment_Website"])
get_db= database.get_database



# Set the Paystack API base URL
paystack_base_url = 'https://api.paystack.co'

import json


# Replace with your Paystack API keys
paystack_secret_key = os.getenv("PAYSTACK_SECRET_KEY")
paystack_public_key = os.getenv("PAYSTACK_PUBLIC_KEY")

# Set the Paystack API base URL
paystack_base_url = 'https://api.paystack.co'

# Define your success and failure redirect URLs
success_url = 'https://yourwebsite.com/success'
failure_url = 'https://yourwebsite.com/failure'

# HTML form for payment
payment_form = f"""
<html>
<head>
    <title>Paystack Payment</title>
</head>
<body>
    <h1>Paystack Payment</h1>
    <form method="POST" action="pay">
        <input type="text" name="amount" placeholder="Amount" required><br>
        <input type="text" name="email" placeholder="Email" required><br>
        <input type="submit" value="Pay">
    </form>
</body>
</html>
"""

@router.post("/pay", response_class=HTMLResponse)
async def initiate_payment(request: Request,amount: int = Form(...), email: str = Form(...),):
    headers = {
        'Authorization': f'Bearer {paystack_secret_key}',
        'Content-Type': 'application/json'
    }

    # Create a Paystack Payment Page
    data = {
        'amount': amount * 100,  # Amount in kobo (100 kobo = 1 Naira)
        'currency': 'NGN',  # Nigerian Naira
        'email': email,
        'metadata': {
            'custom_fields': [
                {
                    'display_name': 'Payment Method',
                    'variable_name': 'payment_method',
                    'value': 'Card'
                }
            ]
        },
        'callback_url': success_url,
    }

    response = requests.post(f'{paystack_base_url}/transaction/initialize', json=data, headers=headers)
    response_data = response.json()

    if response_data['status']:
        authorization_url = response_data['data']['authorization_url']

        # Redirect the customer to Paystack's payment page
        return RedirectResponse(url=authorization_url)
    else:
        # Handle payment initialization failure
        return JSONResponse(content=response_data, status_code=400)

@router.get("/success")
async def payment_success(request: Request, reference: str = None):
    if reference:
        # Verify the payment status using the reference
        headers = {
            'Authorization': f'Bearer {paystack_secret_key}'
        }
        response = requests.get(f'{paystack_base_url}/transaction/verify/{reference}', headers=headers)
        response_data = response.json()

        if response_data['status'] and response_data['data']['status'] == 'success':
            # Payment was successful
            return f"Payment was successful. Reference: {reference}"
    
    # Payment verification failed or no reference provided
    return "Payment verification failed."

@router.get("/failure")
async def payment_failure(request: Request):
    return "Payment failed."

@router.get("/")
async def home(request: Request):
    return HTMLResponse(content=payment_form)