from fastapi import FastAPI, File, UploadFile, Form
from typing import Optional
import os
import uvicorn
from holter import convert_dicom
from pydantic import BaseModel
import shutil

app = FastAPI(
    docs_url="/api/docs", openapi_url="/api"
)

class BufferModel(BaseModel):
    buffer: Optional[bytes] = None

@app.get('/')
def test():
    return 'successful'

@app.post("/api/v1/send-dicom/")
async def senddicom(
    file: UploadFile = File(None),
    buffer: Optional[bytes] = Form(None)
):
    temp_file_path = None
    try:
        temp_dir = "./temp"
        os.makedirs(temp_dir, exist_ok=True)

        if buffer:
            # Handle the buffer
            temp_file_path = os.path.join(temp_dir, "buffer.dcm")
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(buffer)
        elif file:
            # Handle the uploaded file
            temp_file_path = os.path.join(temp_dir, file.filename)
            with open(temp_file_path, "wb") as temp_file:
                shutil.copyfileobj(file.file, temp_file)
        else:
            return {"message": "No file or buffer provided"}

        dicom_json = convert_dicom(temp_file_path)
        return dicom_json
    except Exception as ex:
        print('Exception: ', ex)
        return {"message": "failed"}
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Temporary file {temp_file_path} removed")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8090)
