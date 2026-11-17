from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer,Column,String,Float
from typing import List
from sqlalchemy import ForeignKey, Date
from sqlalchemy.orm import relationship,Mapped,mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__="user"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,index=True)
    name:Mapped[str]=mapped_column(String(50),nullable=False)
    email:Mapped[str]=mapped_column(String(50),unique=True,nullable=False)
    password:Mapped[str]=mapped_column(String(400),nullable=False)
    borrowed_records:Mapped[List["BorrowRecords"]]=relationship("BorrowRecords",back_populates="user") #borrowed_records is python attribute & user is attribute in BorrowRecords class

class Book(Base):
    __tablename__="book"
    id=Column(Integer,primary_key=True,index=True)
    title:Mapped[str]=mapped_column(String(50),nullable=False)
    author:Mapped[str]=mapped_column(String(50),nullable=False)
    price:Mapped[float]=mapped_column(Float,nullable=False)
    available_copies:Mapped[int]=mapped_column(Integer,nullable=False)
    borrowed_records:Mapped[List["BorrowRecords"]]=relationship("BorrowRecords",back_populates="book")

class BorrowRecords(Base):
    __tablename__="borrow_records"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,index=True)
    user_id:Mapped[int]=mapped_column(Integer,ForeignKey("user.id"))
    book_id:Mapped[int]=mapped_column(Integer,ForeignKey("book.id"))
    borrow_date:Mapped[Date]=mapped_column(Date,nullable=False)
    return_date:Mapped[Date]=mapped_column(Date,nullable=True)
    due_date: Mapped[Date] = mapped_column(Date, nullable=False)
    status:Mapped[str]=mapped_column(String(50),nullable=False)
    user = relationship("User", back_populates="borrowed_records")
    book = relationship("Book", back_populates="borrowed_records")

