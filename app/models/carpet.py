from sqlalchemy import Column, String, ForeignKey, BigInteger, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class Carpet(Base):
    __tablename__ = "carpets"

    id = Column(BigInteger, primary_key=True, index=True)
    product_id = Column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    width = Column(Numeric(8, 2), nullable=True)
    length = Column(Numeric(8, 2), nullable=True)
    material = Column(String, nullable=True)
    origin = Column(String, nullable=True)
    age = Column(String, nullable=True)

    # Связи
    product = relationship("Product", back_populates="carpet")
