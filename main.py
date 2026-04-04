from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
from database import engine, get_db
import utils



models.Base.metadata.create_all(bind=engine)

app= FastAPI()

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

