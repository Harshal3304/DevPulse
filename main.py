from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
from database import engine, get_db
import utils
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


models.Base.metadata.create_all(bind=engine)

app= FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "Error": "Wrong Data Format!", 
            "Details": exc.errors()
        }
    )

async def global_exception_handler(request: Request, exc: Exception):
    print(f"DANGER: Server Error -> {exc}") 
    return JSONResponse(
        status_code=500,
        content={
            "Error": "Internal Server Error"
        }
    )

class Developer(BaseModel):
    username:str
    email:str
    github_handle:str
    password:str

    
# POST Request -> (CREATE Endpoint)
@app.post('/developer', status_code=201)
def create_developer(dev: Developer, db: Session = Depends(get_db)):
    existing = db.query(models.Developer).filter(
        (models.Developer.email == dev.email) |
        (models.Developer.username == dev.username)
    ).first()
    if existing:
        if existing.email == dev.email:
            raise HTTPException(
                status_code=409,
                detail=f"Email '{dev.email}' is already registered."
            )
        raise HTTPException(
            status_code=409,
            detail=f"Username '{dev.username}' is already taken."
        )

    hashed_password = utils.hash_password(dev.password)
    new_developer = models.Developer(
        username=dev.username,
        email=dev.email,
        github_handle=dev.github_handle,
        hashed_password = hashed_password
    )
    db.add(new_developer)
    try:
        db.commit()
        db.refresh(new_developer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Duplicate entry — email or username already exists."
        )
    return {"message": "Developer created successfully", "data": new_developer}


# Get all developers -> (GET Endpoint)
@app.get("/developers")
def get_all_developers(db:Session = Depends(get_db)):
    all_devs = db.query(models.Developer).all()
    return {"message":"Developers fetched successfully", "data":all_devs}


# Get specific developer (by username) -> (GET ENDPOINT)
@app.get("/developer/{username}")
def get_single_developer(username:str, db:Session= Depends(get_db)):
    single_dev = db.query(models.Developer).filter(models.Developer.username.lower()== username.lower()).first()
    return {"message":"Developer fetched successfully", "data":single_dev}

# Update developer -> (PUT Endpoint)
@app.put('/developer/{dev_id}')
def update_developer(dev_id:int, dev_data:Developer, db:Session= Depends(get_db)):
    dev= db.query(models.Developer).filter(models.Developer.id== dev_id).first()
    if dev is None:
        return {"message":"Developer not found"}
    
    dev.username = dev_data.username
    dev.email = dev_data.email
    dev.github_handle = dev_data.github_handle

    db.commit()
    db.refresh(dev)
    return {"message":"Developer updated successfully", "data":dev}

# Delete developer -> (DELETE Endpoint)
@app.delete('/developer/{dev_id}')
def delete_developer(dev_id:int,db:Session= Depends(get_db)):
    dev= db.query(models.Developer).filter(models.Developer.id== dev_id).first()
    if dev is None:
        return {"message":"Developer not found"}
    
    db.delete(dev)
    db.commit()
    return {"message":"Developer deleted successfully"}

# Login EndPoint ->
@app.post('/login')
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    dev = db.query(models.Developer).filter(models.Developer.username == user_credentials.username).first()
    
    if not dev:
        raise HTTPException(status_code=403, detail="Invalid Credentials (User nahi mila)")
    if not utils.verify_password(user_credentials.password, dev.hashed_password):
        raise HTTPException(status_code=403, detail="Invalid Credentials (Password galat hai)")
    access_token = utils.create_access_token(data={"sub": dev.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Protected Endpoint 
@app.get("/me")
def get_my_profile(current_user:models.Developer= Depends(utils.get_current_user)):
    return {"message":"Profile fetched successfully", "data":current_user}
