from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class post_source(BaseModel):
    type:str 
    platform: Optional[str] = '' 

class size(BaseModel) :
    url: str
    type: str

class Photo(BaseModel):
    id: int
    text: str
    sizes: list[size]    

class Video(BaseModel):
    id: int
    access_key: str
    owner_id: int
    width: int
    height: int
    

class attachments(BaseModel):
    type: str
    photo: Optional[Photo] = None 
    video: Optional[Video] = None 


class SchPostWall(BaseModel):
    id: int
    owner_id: int
    date: datetime
    text: str
    post_source: post_source
    attachments: list[attachments]

if __name__ == "__main__":
    SchPostWall.model_rebuild()