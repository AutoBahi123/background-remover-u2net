
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import os

app = FastAPI()

@app.post("/remove")
async def remove_background(file: UploadFile = File(...)):
    with open("input.png", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Dummy output for now
    shutil.copy("input.png", "output.png")
    return FileResponse("output.png")
