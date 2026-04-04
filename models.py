from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base

class Developer(Base):
    __tablename__= "developers"

    id= Column(Integer, primary_key= True, index =True)
    username = Column(String, unique= True, index =True)
    email = Column(String, unique= True, index =True)
    github_handle = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

class CommitLog(Base):
    __tablename__= "commit_logs"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    developer_id = Column(Integer, ForeignKey("developers.id"))
    
    