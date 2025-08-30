from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from app.schemas.photo import PhotoOut
from datetime import date
from enum import Enum


class CompanyType(str, Enum):
    funeral_home = "funeral_home"
    logistics_services = "logistics_services"
    burial_care_contractor = "burial_care_contractor"


class CompanyStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class CompanyBase(BaseModel):
    name: str
    short_name: Optional[str] = None
    business_entity: Optional[str] = None
    contract_no: Optional[str] = None
    contract_issue_date: Optional[date] = None
    type: Optional[CompanyType] = None
    status: Optional[CompanyStatus] = CompanyStatus.active


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    name: Optional[str] = None
    pass


class CompanyOut(CompanyBase):
    id: int
    photos: Optional[List[PhotoOut]] = None

    model_config = ConfigDict(from_attributes=True)
