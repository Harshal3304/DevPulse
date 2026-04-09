from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
import models, schemas, utils
from database import get_db
import services

router = APIRouter(
    prefix="/developer",
    tags=["Developer Management"]
)

@router.post('/', status_code=201)
def create_developer(dev: schemas.DeveloperCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Developer).filter(
        (models.Developer.email == dev.email) |
        (models.Developer.username == dev.username)
    ).first()
    
    if existing:
        if existing.email == dev.email:
            raise HTTPException(status_code=409, detail=f"Email '{dev.email}' is already registered.")
        raise HTTPException(status_code=409, detail=f"Username '{dev.username}' is already taken.")

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
        raise HTTPException(status_code=409, detail="Duplicate entry — email or username already exists.")
    return {"message": "Developer created successfully", "data": new_developer}


@router.get("s")
def get_all_developers(db:Session = Depends(get_db)):
    all_devs = db.query(models.Developer).all()
    return {"message":"Developers fetched successfully", "data":all_devs}

@router.get("/{username}")
async def get_single_developer(username: str, db: Session = Depends(get_db)):
    single_dev = db.query(models.Developer).filter(
        func.lower(models.Developer.username) == username.lower()
    ).first()

    if single_dev is None:
        raise HTTPException(status_code=404, detail=f"Developer '{username}' not found")

    github_data = await services.fetch_github_profile(single_dev.github_handle)
    return {"message": "Developer fetched successfully", "data": single_dev, "github_data": github_data}

@router.put('/{dev_id}')
def update_developer(dev_id:int, dev_data: schemas.DeveloperUpdate, db:Session= Depends(get_db)):
    dev= db.query(models.Developer).filter(models.Developer.id== dev_id).first()
    if dev is None:
        raise HTTPException(status_code=404, detail="Developer not found")
    
    dev.username = dev_data.username
    dev.email = dev_data.email
    dev.github_handle = dev_data.github_handle

    db.commit()
    db.refresh(dev)
    return {"message":"Developer updated successfully", "data":dev}

@router.delete('/{dev_id}')
def delete_developer(dev_id:int, db:Session= Depends(get_db)):
    dev= db.query(models.Developer).filter(models.Developer.id== dev_id).first()
    if dev is None:
        raise HTTPException(status_code=404, detail="Developer not found")
    
    db.delete(dev)
    db.commit()
    return {"message":"Developer deleted successfully"}