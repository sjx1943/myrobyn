# crud.py
from sqlalchemy.orm import Session
from models import  Crime


def get_crime(db: Session, crime_id: int):
    return db.query(Crime).filter(Crime.id == crime_id).first()

def get_crimes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Crime).offset(skip).limit(limit).all()

def create_crime(db: Session, crime):
    db_crime = Crime(**crime)
    db.add(db_crime)
    db.commit()
    db.refresh(db_crime)
    return db_crime

def update_crime(db: Session, crime_id: int, crime):
    db_crime = get_crime(db, crime_id)
    if db_crime is None:
        return None
    for key, value in crime.items():
        setattr(db_crime, key, value)
    db.commit()
    db.refresh(db_crime)
    return db_crime

def delete_crime(db: Session, crime_id: int):
    db_crime = get_crime(db, crime_id)
    if db_crime is None:
        return False
    db.delete(db_crime)
    db.commit()
    return True

