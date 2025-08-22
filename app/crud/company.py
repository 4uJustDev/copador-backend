from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate
from typing import Optional, List


def get_company(db: Session, company_id: int) -> Optional[Company]:
    """Получить компанию по ID"""
    try:
        return db.query(Company).filter(Company.id == company_id).first()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_companies(db: Session, skip: int = 0, limit: int = 100) -> List[Company]:
    """Получить список компаний с пагинацией"""
    try:
        return db.query(Company).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_company_by_name(db: Session, name: str) -> Optional[Company]:
    """Получить компанию по названию"""
    try:
        return db.query(Company).filter(Company.name == name).first()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def create_company(db: Session, company: CompanyCreate) -> Company:
    """Создать новую компанию"""
    try:
        db_company = Company(**company.dict())
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        return db_company
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def update_company(
    db: Session, company_id: int, company: CompanyUpdate
) -> Optional[Company]:
    """Обновить компанию"""
    try:
        db_company = get_company(db, company_id)
        if not db_company:
            return None

        update_data = company.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_company, field, value)

        db.commit()
        db.refresh(db_company)
        return db_company
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def delete_company(db: Session, company_id: int) -> bool:
    """Удалить компанию"""
    try:
        db_company = get_company(db, company_id)
        if db_company:
            db.delete(db_company)
            db.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        raise e
