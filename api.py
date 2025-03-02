# -----------------------------------------------------
#
#     API
#
# -----------------------------------------------------

import os
import jwt
import datetime
from fastapi import FastAPI, Query, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# import mysql.connector
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()



USER_MYSQL = os.getenv("USER_MYSQL")
PASSWORD_MYSQL = os.getenv("PASSWORD_MYSQL")

SECRET_KEY = os.getenv("SECRET_KEY")
API_PASSWORD = os.getenv("API_PASSWORD")

print(USER_MYSQL, PASSWORD_MYSQL, SECRET_KEY, API_PASSWORD)

app = FastAPI()



@app.get("/")
# async def root():
def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)





