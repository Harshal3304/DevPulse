from fastapi import FastAPI 

app= FastAPI()

@app.get('/')
def home():
    return {"message": "DevPulse API"}

@app.get('/health')
def health_check():
    return {'status':"ok"}

@app.get('/developer/{username}')
def get_developer(username:str):
    return {'username':username}

