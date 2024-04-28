import datetime
from typing import Any

from sqlalchemy.orm import Session

from . import models


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

    def add_one(self, model: Any):
        assert type(model) == self._model_class

        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)

        return model


class PostsRepository(RepositoryBase):
    def __init__(self, db: Session, default_id_field: str | None = "id"):
        super().__init__(db, models.Posts, default_id_field)

    def create_one(self, post: Any):
        db_post = models.Posts(
            title=post.title,
            text=post.text,
            user_id=post.user_id,
            creation_time=datetime.datetime.now(),
        )

        return self.add_one(db_post)
    
    def get_with_pagination(self, user_id: int, start_id: int, count_limit: int):
        return self._db.query(self._model_class) \
            .filter(getattr(self._model_class, "user_id") == user_id) \
            .filter(getattr(self._model_class, "id") >= start_id) \
            .limit(count_limit)
