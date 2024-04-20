import datetime
import hashlib
from typing import Any

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from pydantic import BaseModel

from . import models, schemas


def get_password_hash(username: str, password: str):
    return hashlib.sha256((password+username).encode()).hexdigest()

def generate_secret(username: str, password: str):
    return hashlib.sha256((password+username+str(datetime.datetime.now().timestamp())).encode()).hexdigest()


class RepositoryBase:
    def __init__(self, db: Session, model_class: object, default_id_field: str | None = "id"):
        if default_id_field is not None:
            assert hasattr(model_class, default_id_field)

        self._db = db
        self._model_class = model_class
        self._default_id_field = default_id_field
    
    def commit(self):
        return self._db.commit()

    def get_all(self):
        return self._db.query(self._model_class).all()
    
    def get_one(self, id: Any, id_field: str | None = None):
        id_field = id_field or self._default_id_field
        assert hasattr(self._model_class, id_field)

        return self._db.query(self._model_class).filter(getattr(self._model_class, id_field) == id).first()

    def check_exists(self, id: Any, id_field: str | None = None):
        id_field = id_field or self._default_id_field
        assert hasattr(self._model_class, id_field)

        return self._db.query(self._model_class).filter(getattr(self._model_class, id_field) == id).count() > 0

    def delete_one(self, id: Any, id_field: str | None = None):
        id_field = id_field or self._default_id_field
        assert hasattr(self._model_class, id_field)

        try:
            deleted_count = self._db.query(self._model_class).filter(getattr(self._model_class, id_field) == id).delete()
            self._db.commit()
        except:
            return 0

        return deleted_count

    def add_one(self, model: BaseModel):
        assert type(model) == self._model_class

        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)

        return model


class UsersRepository(RepositoryBase):
    def __init__(self, db: Session):
        super().__init__(db, models.Users, default_id_field="username")

    def create_one(self, user_info: schemas.RegistrationInput):
        if self.check_exists(user_info.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

        user_info.password = get_password_hash(user_info.username, user_info.password)
        db_user = models.Users(
            **user_info.model_dump(),
            creation_time=datetime.datetime.now(),
        )

        return self.add_one(db_user)
    
    def update_one(self, username: str, user_info: schemas.UserUpdateInput):
        if not self.check_exists(username):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Username not found")

        db_user = self.get_one(username)

        db_user.first_name = user_info.first_name
        db_user.second_name = user_info.second_name
        db_user.birth_date = user_info.birth_date
        db_user.email = user_info.email
        db_user.phone_number = user_info.phone_number

        return self.commit()

    def validate_one(self, auth: schemas.AuthInput):
        if not self.check_exists(auth.username):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Username not found")

        db_user = self.get_one(auth.username)

        return db_user.password == get_password_hash(auth.username, auth.password)


class SessionsRepository(RepositoryBase):
    def __init__(self, db: Session):
        super().__init__(db, models.Sessions, default_id_field="secret")
    
    def create_one(self, auth: schemas.AuthInput):
        while True:
            secret = generate_secret(auth.username, auth.password)
            if not self.check_exists(secret):
                break

        db_session = models.Sessions(
            username=auth.username,
            secret=secret,
            creation_time=datetime.datetime.now(),
        )
        self.add_one(db_session)

        return secret

    def validate_one(self, secret: str):
        if not self.check_exists(secret):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
        
        db_session = self.get_one(secret)

        return db_session.username
