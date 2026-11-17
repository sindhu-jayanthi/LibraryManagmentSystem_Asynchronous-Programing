from fastapi import FastAPI , Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from Database_Models import Base,Book,User,BorrowRecords
from Data_Models import *
from sqlalchemy import select
from contextlib import asynccontextmanager
from Database import get_db,async_sessionmaker,SessionLocal,engine
from sqlalchemy.exc import SQLAlchemyError
from security import hash_password
import string
from datetime import date,timedelta


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    await engine.dispose()




app = FastAPI(lifespan=lifespan)




@app.post("/books/", response_model=BookResponse)
async def create_book(
    data: BookCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        print("1. POST request received")

        query = select(Book).where(Book.title == data.title)
        result = await db.execute(query)

        print("2. Database query executed")

        check_book = result.scalar_one_or_none()

        if check_book:
            raise HTTPException(
                status_code=400,
                detail="Book already exists"
            )


        new_book = Book(**data.model_dump())

        db.add(new_book)

        print("3. Book added to session")

        await db.commit()

        print("4. Transaction committed")

        await db.refresh(new_book)

        print("5. Book refreshed")

        return new_book

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        await db.rollback()
        print("DATABASE ERROR:", repr(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.get("/books/", response_model=list[BookResponse])
async def get_books(db: AsyncSession=Depends(get_db)):
        query = select(Book).order_by(Book.id.asc())
        result=await db.execute(query)
        books = result.scalars().all()
        return books
@app.get("/books/{id}", response_model=BookResponse)
async def get_book_By_id(id:int,db: AsyncSession=Depends(get_db)):

    query=select(Book).where (Book.id==id)
    result=await db.execute(query)
    book=result.scalars().one_or_none()
    if book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )
    return book
@app.put("/books/{id}", response_model=BookResponse)
async def update_book(id:int,data:BookUpdate,db: AsyncSession=Depends(get_db)):
        query=select(Book).where(Book.id==id)
        result=await db.execute(query)
        updated_book=result.scalars().one()
        if updated_book is None:
            raise HTTPException(
                status_code=404,
                detail="Book not found"
            )

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
                setattr(updated_book, key, value)
        await db.commit()
        await db.refresh(updated_book)


        return updated_book
@app.delete("/books/{id}")
async def delete_book(id:int,db: AsyncSession=Depends(get_db)):
    query=select(Book).where(Book.id==id)
    result=await db.execute(query)
    del_book=result.scalars().one_or_none()
    if del_book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )
    await db.delete(del_book)
    await db.commit()
    return {"message": "Book deleted successfully"}

@app.post("/users/", response_model=UserResponse)
async def create_user(data:UserCreate,db : AsyncSession=Depends(get_db)):

    query=select(User).where(User.email==data.email)
    result=await db.execute(query)
    user = result.scalar_one_or_none()

    if user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )
    new_user=User( name=data.name,
    email=data.email,
    password=hash_password(data.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@app.get("/users/", response_model=list[UserResponse])
async def get_users(db: AsyncSession=Depends(get_db)):
    query=select(User).order_by(User.id.asc())
    result=await db.execute(query)
    users = result.scalars().all()
    return users

@app.get("/users/{id}", response_model=UserResponse)
async def get_user(id:int,db: AsyncSession=Depends(get_db)):
    query=select(User).where(User.id==id)
    result=await db.execute(query)
    user=result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user
@app.put("/users/{email}", response_model=UserUpdate)
async def update_user(email:str,data:UserUpdate,db: AsyncSession=Depends(get_db)):
    query=select(User).where(User.email==data.email)
    result=await db.execute(query)
    updated_user=result.scalar_one_or_none()
    if updated_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(updated_user, key, value)
    await db.commit()
    await db.refresh(updated_user)
    return updated_user
@app.delete("/users/{id}")
async def delete_user(id:int,db: AsyncSession=Depends(get_db)):
    query=select(User).where(User.id==id)
    result=await db.execute(query)
    del_user=result.scalar_one_or_none()
    if del_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    await db.delete(del_user)
    await db.commit()
    return {"message": "User deleted successfully"}

@app.post("/borrowrecords/")
async def borrow_record_create(data: BorrowRecordCreate,db:AsyncSession = Depends(get_db)):
    query=select(User).where(User.id==data.user_id)
    result=await db.execute(query)
    user_record=result.scalar_one_or_none()
    if user_record is None:
        raise HTTPException(
            status_code=400,
            detail="User not found"
        )
    query=select(Book).where(Book.id==data.book_id)
    result = await db.execute(query)
    book_record = result.scalar_one_or_none()
    if book_record is None:
        raise HTTPException(
            status_code=400,
            detail="Book not found"
        )
    if book_record.available_copies<=0:
        raise HTTPException(
            status_code=400,
            detail="Copies are not available"
        )
    borrow_date = date.today()
    due_date = borrow_date + timedelta(days=14)

    new_borrow_record=BorrowRecords(
        user_id=data.user_id,
        book_id=data.book_id,
        borrow_date= borrow_date,
        due_date= due_date,
        return_date=None,
        status="Borrowed"
    )
    book_record.available_copies -= 1
    db.add(new_borrow_record)
    await db.commit()
    await db.refresh(new_borrow_record)
    return new_borrow_record
@app.get("/borrowrecords/", response_model=list[BorrowRecordResponse])
async def get_borrowed_records(db: AsyncSession = Depends(get_db)):
    query=select(BorrowRecords).order_by(BorrowRecords.borrow_date.desc(),BorrowRecords.id.desc())
    result=await db.execute(query)
    borrowed_records=result.scalars().all()
    return borrowed_records

@app.get("/borrowrecords/overdue",response_model=list[BorrowRecordResponse])
async def get_overdue_records(db: AsyncSession = Depends(get_db)):

    query = select(BorrowRecords).where( BorrowRecords.due_date<date.today() , BorrowRecords.status=="Borrowed")
    result = await db.execute(query)
    overdue_records = result.scalars().all()

    return overdue_records

@app.get("/borrowrecords/{id}",response_model=list[BorrowRecordResponse])
async def get_borrowed_records_by_userid(id:int,db: AsyncSession = Depends(get_db)):
    query=select(User).where(User.id ==id)
    result=await db.execute(query)
    user_record=result.scalar_one_or_none()
    if user_record is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    query=select(BorrowRecords).where(BorrowRecords.user_id==id)
    result=await db.execute(query)
    borrowed_records=result.scalars().all()
    return borrowed_records




@app.put("/borrowrecords/{id}/return", response_model=BorrowRecordResponse)
async def return_record(id:int,db: AsyncSession = Depends(get_db)):
    query=select(BorrowRecords).where (BorrowRecords.id==id)
    result=await db.execute(query)
    borrowed_record=result.scalar_one_or_none()
    if borrowed_record is None:
        raise HTTPException(
            status_code=404,
            detail="borrow record not found"
        )
    if borrowed_record.status == "Returned":
        raise HTTPException(
            detail="Borrow record already Returned",
            status_code=409
        )

    borrowed_record.status = "Returned"
    borrowed_record.return_date = date.today()

    query=select(Book).where(Book.id==borrowed_record.book_id)
    result=await db.execute(query)
    result=result.scalar_one_or_none()
    result.available_copies+=1
    await db.commit()
    await db.refresh(borrowed_record)
    return borrowed_record

@app.get("/books/search", response_model=list[BookResponse]) #query parameter /books/search?title=Python; /books/search/{title} - path parameter.Here queru parameter is suggested sinch its changes the url
async def search_books( title: str,db: AsyncSession = Depends(get_db)):
    query = select(Book).where( Book.title.ilike(f"%{title}%"))
    result = await db.execute(query)
    books = result.scalars().all()

    return books
