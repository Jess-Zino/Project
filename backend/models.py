# models.py

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    hashed_pin = Column(String, nullable=False)

class Equation(Base):
    __tablename__ = "equations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    latex = Column(String)
    mathml = Column(String)
    nemeth = Column(String)