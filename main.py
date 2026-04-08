from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models, utils
from database import engine, get_db
from routers import developer 

models.Base.metadata.create_all(bind=engine)

app= FastAPI(title="DevPulse API")

app.include_router(developer.router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"Error": "Wrong Data Format!", "Details": exc.errors()}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"DANGER: Server Error -> {exc}") 
    return JSONResponse(
        status_code=500,
        content={"Error": "Internal Server Error"}
    )

@app.post('/login', tags=["Authentication"])
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    dev = db.query(models.Developer).filter(models.Developer.username == user_credentials.username).first()
    
    if not dev or not utils.verify_password(user_credentials.password, dev.hashed_password):
        raise HTTPException(status_code=403, detail="Invalid Credentials")
        
    access_token = utils.create_access_token(data={"sub": dev.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", tags=["Authentication"])
def get_my_profile(current_user: models.Developer = Depends(utils.get_current_user)):
    return {"message": "Profile fetched successfully", "data": current_user}