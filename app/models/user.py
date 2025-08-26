from sqlalchemy import (
    Column,
    DateTime,
    Date,
    Text,
    BigInteger,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(Text, unique=True, nullable=True)  # может быть NULL для соцсетей
    password_hash = Column(Text, nullable=True)  # может быть NULL для соцсетей
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    providers = relationship(
        "UserProvider", back_populates="user", cascade="all, delete-orphan"
    )
    user_roles = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def roles(self):
        """Получить список ролей пользователя"""
        return [user_role.role for user_role in self.user_roles]

    @property
    def role_names(self):
        """Получить список названий ролей пользователя"""
        return [user_role.role.name for user_role in self.user_roles]


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    first_name = Column(Text, nullable=True)
    last_name = Column(Text, nullable=True)
    phone = Column(Text, nullable=True)
    birth_date = Column(Date, nullable=True)
    avatar_url = Column(Text, nullable=True)

    # Связь с пользователем
    user = relationship("User", back_populates="profile")


class UserProvider(Base):
    __tablename__ = "user_providers"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    provider = Column(Text, nullable=False)  # 'google', 'apple', 'facebook'
    provider_user_id = Column(Text, nullable=False)  # ID в системе провайдера

    # Связь с пользователем
    user = relationship("User", back_populates="providers")


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id = Column(
        BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )

    # Связи
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
