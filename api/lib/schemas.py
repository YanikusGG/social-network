from pydantic import BaseModel


class AuthInput(BaseModel):
    username: str
    password: str


class RegistrationInput(BaseModel):
    username: str
    password: str

    first_name: str
    second_name: str
    birth_date: str
    email: str
    phone_number: str


class SecretHandler(BaseModel):
    secret: str


class UserUpdateInput(SecretHandler):
    first_name: str
    second_name: str
    birth_date: str
    email: str
    phone_number: str


class CreatePostInput(BaseModel):
    title: str
    text: str


class UpdatePostInput(BaseModel):
    id: int
    title: str
    text: str


class DeletePostInput(BaseModel):
    id: int


class GetPostInput(BaseModel):
    id: int


class GetUserPostsInput(BaseModel):
    user_id: int
    start_id: int
