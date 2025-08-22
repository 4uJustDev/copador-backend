from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)

    firstname = Column(String, nullable=True)
    lastname  = Column(String, nullable=True)
    phone     = Column(String, nullable=True)
    email     = Column(String, nullable=True)

    company = relationship("Company", back_populates="contacts")
