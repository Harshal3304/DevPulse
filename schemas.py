from pydantic import BaseModel

class DeveloperCreate(BaseModel):
    username:str
    email:str
    github_handle:str
    password:str

class DeveloperUpdate(BaseModel):
    username:str
    email:str
    github_handle:str

