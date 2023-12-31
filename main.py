from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing_extensions import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    #allow_credentials=True
    #allow_methods=["*"],
    #allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

class PostBase(BaseModel):
    title: str
    content:str
    user_id: int 

class UserBase(BaseModel):
    username: str 


def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()


db_dependency = Annotated[(Session, Depends(get_db))]

@app.put("/posts/{post_id}", status_code=status.HTTP_201_CREATED)
async def update_post(post_id: int, new_post: PostBase, db: db_dependency):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail='Post was not found')
    db_post.title = new_post.title
    db_post.content = new_post.content
    db_post.user_id = new_post.user_id
    db.commit()


@app.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostBase, db:db_dependency):
    db_post = models.Post(**post.dict())
    db.add(db_post)
    db.commit()

@app.get("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def read_post(post_id: int, db: db_dependency):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail='Post was not found')
    return post


@app.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(post_id: int, db: db_dependency):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail='Post was not found')
    db.delete(db_post)
    db.commit()

@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()

@app.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return user

