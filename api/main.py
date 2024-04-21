from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from sqlalchemy.orm import Session

import os
import grpc
import google.protobuf.json_format as json_format

from lib import crud, schemas
from lib.database import get_db

from lib.proto import social_engine_pb2 as pb
from lib.proto import social_engine_pb2_grpc as pb_service

SOCIAL_ENGINE_GRPC_URL = os.environ.get('SOCIAL_ENGINE_GRPC_URL')

def get_social_engine_stub():
    grpc_client_channel = grpc.insecure_channel(SOCIAL_ENGINE_GRPC_URL)
    stub = pb_service.SocialEngineStub(grpc_client_channel)
    yield stub

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


@app.post("/post/create")
def create_post(secret: str, post_input: schemas.CreatePostInput, db: Session = Depends(get_db), stub = Depends(get_social_engine_stub)):
    '''
    create new post with given data
    '''

    try:
        session_repository = crud.SessionsRepository(db)
        username = session_repository.validate_one(secret)

        users_repository = crud.UsersRepository(db)
        user_id = users_repository.get_id_by_username(username)

        post_request = pb.PostRequest()
        post_request.post.title = post_input.title
        post_request.post.text = post_input.text
        post_request.post.user_id = user_id
        post_request.request_user_id = user_id

        post_response = stub.CreatePost(post_request)

        if post_response.code != 200:
            raise HTTPException(status_code=post_response.code, detail=post_response.description)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect input for create post")

    return {
        'id': post_response.post.id,
        'creation_time': post_response.post.creation_time.seconds
    }


@app.post("/post/update")
def update_post(secret: str, post_input: schemas.UpdatePostInput, db: Session = Depends(get_db), stub = Depends(get_social_engine_stub)):
    '''
    update post with given id and data
    '''

    try:
        session_repository = crud.SessionsRepository(db)
        username = session_repository.validate_one(secret)

        users_repository = crud.UsersRepository(db)
        user_id = users_repository.get_id_by_username(username)

        post_request = pb.PostRequest()
        post_request.post.id = post_input.id
        post_request.post.title = post_input.title
        post_request.post.text = post_input.text
        post_request.post.user_id = user_id
        post_request.request_user_id = user_id

        post_response = stub.UpdatePost(post_request)

        if post_response.code != 200:
            raise HTTPException(status_code=post_response.code, detail=post_response.description)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect input for update post")

    return {}


@app.delete("/post/delete")
def delete_post(secret: str, id: int, db: Session = Depends(get_db), stub = Depends(get_social_engine_stub)):
    '''
    delete post with given id
    '''

    try:
        session_repository = crud.SessionsRepository(db)
        username = session_repository.validate_one(secret)

        users_repository = crud.UsersRepository(db)
        user_id = users_repository.get_id_by_username(username)

        post_request = pb.PostRequest()
        post_request.post.id = id
        post_request.post.user_id = user_id
        post_request.request_user_id = user_id

        post_response = stub.DeletePost(post_request)

        if post_response.code != 200:
            raise HTTPException(status_code=post_response.code, detail=post_response.description)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect input for delete post")

    return {}


@app.get("/post/get")
def get_post(secret: str, id: int, db: Session = Depends(get_db), stub = Depends(get_social_engine_stub)):
    '''
    get post with given id
    '''

    try:
        session_repository = crud.SessionsRepository(db)
        username = session_repository.validate_one(secret)

        users_repository = crud.UsersRepository(db)
        user_id = users_repository.get_id_by_username(username)

        post_request = pb.PostRequest()
        post_request.post.id = id
        post_request.request_user_id = user_id

        post_response = stub.GetPost(post_request)

        if post_response.code != 200:
            raise HTTPException(status_code=post_response.code, detail=post_response.description)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect input for get post")

    return {
        'id': post_response.post.id,
        'title': post_response.post.title,
        'text': post_response.post.text,
        'user_id': post_response.post.user_id,
        'creation_time': post_response.post.creation_time.seconds,
    }


@app.get("/post/all/get")
def get_all_posts(secret: str, user_id: int, start_id: int, db: Session = Depends(get_db), stub = Depends(get_social_engine_stub)):
    '''
    get all posts with given user and pagination
    '''

    try:
        session_repository = crud.SessionsRepository(db)
        username = session_repository.validate_one(secret)

        users_repository = crud.UsersRepository(db)
        request_user_id = users_repository.get_id_by_username(username)

        post_request = pb.PostRequest()
        post_request.post.user_id = user_id
        post_request.post.id = start_id
        post_request.request_user_id = request_user_id

        last_error_response = None
        final_response = {
            'user_id': user_id,
            'posts': []
        }
        for post_response in stub.GetUserPosts(post_request):
            if post_response.code != 200:
                last_error_response = HTTPException(status_code=post_response.code, detail=post_response.description)
            else:
                final_response['posts'].append({
                    'id': post_response.post.id,
                    'title': post_response.post.title,
                    'text': post_response.post.text,
                    'creation_time': post_response.post.creation_time.seconds,
                })

        if last_error_response:
            raise last_error_response
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect input for get all posts")

    return final_response
