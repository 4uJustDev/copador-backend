from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)

    filename  = Column(String, nullable=False)
    filepath  = Column(Text,   nullable=False)
    thumbpath = Column(Text,   nullable=False)

    company = relationship("Company", back_populates="photos")
