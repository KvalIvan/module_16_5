from fastapi import FastAPI, HTTPException, Path, Request, Form
from pydantic import BaseModel, Field
from typing import List, Annotated
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


class User(BaseModel):
    id: int
    username: str = Field(..., min_length=5, max_length=15, description='Enter username')
    age: int = Field(ge=18, le=100, description='Enter age')


app = FastAPI(swagger_ui_parameters={'tryItOutEnabled': True}, debug=True)
templates = Jinja2Templates(directory='templates')

users: List[User] = []


@app.get('/')
async def welcome(request: Request) -> HTMLResponse:
    return templates.TemplateResponse('users.html', {'request': request, 'users': users})


@app.get('/user/{user_id}', response_class=HTMLResponse)
async def get_users(request: Request, user_id: Annotated[int, Path(ge=0, description='Enter id')]):
    for user in users:
        if user.id == user_id:
            return templates.TemplateResponse('users.html', {'request': request, 'user': user})
    else:
        raise HTTPException(status_code=404, detail='User not found')


@app.post('/')
async def create_user(request: Request, username: str = Form(), age: int = Form()) -> HTMLResponse:
    new_id = max(u.id for u in users) + 1 if users else 1
    new_user = User(id=new_id, username=username, age=age)
    users.append(new_user)
    return templates.TemplateResponse('users.html', {'request': request, 'users': users})


@app.put('/user/{user_id}/{username}/{age}', response_model=User)
async def update_user(user_id: int, username: str, age: int) -> User:
    for user in users:
        if user.id == user_id:
            user.username = username
            user.age = age
            return user
    raise HTTPException(status_code=404, detail='id not found')


@app.delete('/user/{user_id}', response_model=User)
async def delete_user(user_id: int) -> User:
    for i, u in enumerate(users):
        if u.id == user_id:
            return users.pop(i)
    raise HTTPException(status_code=404, detail='id not found')
