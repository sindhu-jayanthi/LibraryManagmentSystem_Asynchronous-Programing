from pydantic import BaseModel,ConfigDict,field_validator,Field
from datetime import date
import re

class UserCreate(BaseModel):
    name: str
    email: str
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain an uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain a lowercase letter")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain a number")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=]", value):
            raise ValueError("Password must contain a special character")

        return value

class UserResponse(BaseModel):
    id: int
    #user_id: int
    #book_id: int
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)
class UserUpdate(BaseModel):
    name: str | None = None
    email: str
    model_config = ConfigDict(from_attributes=True)

class BookCreate(BaseModel):
    title: str
    author: str
    price: float
    available_copies: int

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    price: float
    available_copies: int
    model_config = ConfigDict(from_attributes=True)

class BookUpdate(BaseModel):

    title: str | None = None
    author: str | None = None
    price: float |None  = None
    available_copies: int | None = None


class BorrowRecordCreate(BaseModel):
    user_id: int
    book_id: int


class BorrowRecordResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrow_date: date
    due_date :date
    return_date: date | None = None

    status: str

    model_config = ConfigDict(from_attributes=True)





