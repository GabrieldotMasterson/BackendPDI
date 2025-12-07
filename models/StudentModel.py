from datetime import datetime, timezone

from factory import db
from pydantic import BaseModel
from typing import Optional
from utils.models import OrmBase



from models.RoleModel import Role, RoleResponse

class Student(db.Model):
    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)

    # Dados acadêmicos
    enrollment_year = db.Column(db.Integer)
    course = db.Column(db.String(128))
    current_module = db.Column(db.String(64))

    # Dados analisados pela IA
    mood = db.Column(db.Float)
    dedication_score = db.Column(db.Float)
    strengths = db.Column(db.Text)
    improvements = db.Column(db.Text)
    last_insights = db.Column(db.Text)
    last_analysis_date = db.Column(db.DateTime)

    # Métricas para dashboards
    completed_todos = db.Column(db.Integer, default=0)
    total_todos = db.Column(db.Integer, default=0)
    pdicount = db.Column(db.Integer, default=0)
    risk_score = db.Column(db.Float)

    # Relacionamentos
    pdis = db.relationship("PDI", backref="student", cascade="all, delete-orphan")
    weekly_forms = db.relationship("WeeklyForm", backref="student", cascade="all, delete-orphan")
    todos = db.relationship("Todo", backref="student", cascade="all, delete-orphan")
