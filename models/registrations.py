from app import db
from datetime import datetime, timezone
from utils.models import OrmBase, BaseModel

class Registrations(db.Model):
    __tablename__ = "registrations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    talk_id = db.Column(
        db.Integer,
        db.ForeignKey("talks.id", ondelete="CASCADE"),
        nullable=False
    )
    registered_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("user_id", "talk_id", name="unique_user_talk_id"),
    )

    def __repr__(self) -> str:
        return f"<Registrations {self.name}>"
    

class RegisterUserInTalk(BaseModel):
    user_id: int
    talk_id: int

class RegistrationsResponses(RegisterUserInTalk):
    registered_at: datetime

class UnregisterUserInTalk(RegisterUserInTalk):
    pass

