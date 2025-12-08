from datetime import datetime, timezone

from app import db
from pydantic import BaseModel
from typing import Optional
from utils.models import OrmBase

from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash

from models.RoleModel import Role, RoleResponse


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    username = db.Column(db.String(64), nullable=False, index=True)
    password_hash = db.Column(db.String(256), index=True)
    email = db.Column(db.String(128), unique=True, nullable=False, index=True)
    birthdate = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    role = db.relationship("Role", back_populates="users")

    registrations = db.relationship(
        "Registrations",
        backref=db.backref("user", passive_deletes=True),
        cascade="all, delete-orphan"
    )


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        if self.role is None:
            self.role = db.session.scalars(select(Role).filter_by(name="user")).first()

    @property
    def password(self):
        raise AttributeError("Senha é um valor protegido")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class UserEdit(BaseModel):
    username: str
    email: str
    password: str

class UserCreate(UserEdit):
    pass


class UserResponse(OrmBase):
    username: str
    email: str
    birthdate: Optional[datetime]
    created_at: datetime
    role: RoleResponse


class UserResponseList(BaseModel):
    users: list[UserResponse]


class UserResponseSimple(OrmBase):
    username: str


