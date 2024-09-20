from typing import Optional

from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from pydantic import EmailStr, BaseModel


class UserSignUp(BaseModel):
    username: str
    email: EmailStr
    password: str


class UsersRepository:
    def __init__(self):
        self.users = []

    def add_user(self, user_data):
        if any(user == user_data['email'] for user in self.users):
            raise HTTPException(status_code=400, detail='Email already')
        self.users.append(user_data)
        return user_data

users_repo = UsersRepository()

@app.post('/signup', status_code=200)
async def signup(
    username: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    profile_picture = Optional[UploadFile] = File(None)
):
    if profile_picture:
        file_location = f"profile_pictures/{profile_picture.filename}"
        with open(file_location, 'cm') as buffer:
            shutil.copyfileobj(profile_picture.file, buffer)
    else:
        file_location = None

    new_user = {
        'username': username,
        'email': email,
        'password': passwords,
        'profile_picture': profile_picture,
    }

    try:
        saved_user = users_repo.add_user(new_user)
    except HTTPException as e:
        raise e

    return {saved_user}



