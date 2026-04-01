from fastapi import FastAPI 
from pydantic import BaseModel

app= FastAPI()

class Developer(BaseModel):
    username:str
    email:str
    github_handle:str
    

@app.get('/')
def home():
    return {"message": "DevPulse API"}

@app.get('/health')
def health_check():
    return {'status':"ok"}

@app.get("/developer")
def list_developer(limit: int = 10, active: bool = True):
    return {"limit": limit, "active": active}

@app.get("/commits")
def get_commits(username:str, limit:int=10, page:int=1):
    skip = (page-1)*limit
    return {"username":username, "limit":limit, "page":page, "skip":skip}    

@app.get('/developer/{username}')
def get_developer(username:str):
    return {'username':username} 

@app.post('/developer')
def create_developer(dev: Developer):
    return {"message": f"developer {dev.username} registered successfully", "data": dev}
