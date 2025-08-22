from sqlalchemy import Column, Integer, String, Date, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class CompanyType(str, enum.Enum):
    funeral_home = "funeral_home"
    logistics_services = "logistics_services"
    burial_care_contractor = "burial_care_contractor"


class CompanyStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    short_name = Column(String, nullable=True, index=True)
    business_entity = Column(String, nullable=True)

    contract_no = Column(String, nullable=True)
    contract_issue_date = Column(Date, nullable=True)

    type = Column(Enum(CompanyType), nullable=True)
    status = Column(Enum(CompanyStatus), default=CompanyStatus.active)

    # связи на будущее
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="company", cascade="all, delete-orphan")
