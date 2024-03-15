from sqlalchemy import Column, Integer, String, TIMESTAMP

from .database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    creation_time = Column(TIMESTAMP, nullable=False)
    first_name = Column(String)
    second_name = Column(String)
    birth_date = Column(String)
    email = Column(String)
    phone_number = Column(String)


class Sessions(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    secret = Column(String, nullable=False, unique=True)
    creation_time = Column(TIMESTAMP, nullable=False)
