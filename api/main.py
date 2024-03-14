from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from sqlalchemy.orm import Session

from lib import crud, schemas
from lib.database import get_db

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


@app.get("/docs")
def read_docs():
    '''
    get swagger documentation html
    '''

    return get_swagger_ui_html(openapi_url="/openapi.json")


@app.post("/auth/signup")
def create_user(user_info: schemas.RegistrationInput, db: Session = Depends(get_db)):
    '''
    create new user with given data
    '''

    try:
        users_repository = crud.UsersRepository(db)
        users_repository.create_one(user_info)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect input for signup")

    return {}


@app.post("/auth/update")
def update_user(user_info: schemas.UserUpdateInput, db: Session = Depends(get_db)):
    '''
    update user with given data
    '''

    try:
        session_repository = crud.SessionsRepository(db)
        username = session_repository.validate_one(user_info.secret)

        users_repository = crud.UsersRepository(db)
        users_repository.update_one(username, user_info)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect input for update")

    return {}

@app.post("/auth/signin")
def create_session(auth: schemas.AuthInput, db: Session = Depends(get_db)):
    '''
    create new session with given data and return secret
    '''

    try:
        users_repository = crud.UsersRepository(db)
        assert users_repository.validate_one(auth)

        session_repository = crud.SessionsRepository(db)
        secret = session_repository.create_one(auth)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect input for signin")

    return {"secret": secret}
