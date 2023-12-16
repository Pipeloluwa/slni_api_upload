import os
from fastapi.responses import FileResponse
import uuid
from .import s3Bucket
import time
from . import s3Bucket
import uuid

IMAGEDIR= "media/images/"
async def show_image():
    files= os.listdir(IMAGEDIR)
    path= f"{IMAGEDIR}{files[0]}"
    return FileResponse(path)


BASE_DIR= os.path.dirname(os.path.abspath("\media"))
UPLOAD_DIR= os.path.join(BASE_DIR, "images")
timestr= time.strftime("%Y%m%d-%H%M%S")

async def names_process(file):   
    file=f"{uuid.uuid4()}-{timestr}{os.path.splitext(file.filename)[1]}"     
    return  (file)

