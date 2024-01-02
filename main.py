from fastapi import FastAPI, Depends
from fastapi.openapi.models import Contact
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import HTTPException
from typing import List

app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///./contacts.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone_number = Column(String)
    birth_date = Column(Date)
    additional_info = Column(String, nullable=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)


class ContactCreate:
    pass


@app.post("/contacts/", response_model=Contact)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    new_contact = Contact(**contact.dict())
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


@app.get("/contacts/", response_model=List[Contact])
def get_all_contacts(db: Session = Depends(get_db)):
    return db.query(Contact).all()


@app.put("/contacts/{contact_id}", response_model=Contact)
def update_contact(contact_id: int, contact: ContactCreate, db: Session = Depends(get_db), get_db=None):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    for key, value in contact.dict().items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@app.delete("/contacts/{contact_id}", response_model=dict)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(db_contact)
    db.commit()
    return {"message": "Contact deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)