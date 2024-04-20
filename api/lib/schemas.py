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


class UserUpdateInput(BaseModel):
    secret: str

    first_name: str
    second_name: str
    birth_date: str
    email: str
    phone_number: str
