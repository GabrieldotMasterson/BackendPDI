from datetime import datetime, timezone
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

from factory import db
from utils.models import OrmBase
from models.UserModel import UserResponseSimple

class TaskType(str, Enum):
    ESTUDO = "estudo"
    PRATICA = "pratica"
    ANALISE = "analise"
    DESENVOLVIMENTO = "desenvolvimento"
    REVISAO = "revisao"


class Task(db.Model):
    __tablename__ = "pdi_Tasks"

    id = db.Column(db.Integer, primary_key=True)

    meta_id = db.Column(
        db.Integer,
        db.ForeignKey("pdi_metas.id", ondelete="CASCADE"),
        nullable=False
    )
    pdi_id = db.Column(
        db.Integer,
        db.ForeignKey("pdi.id", ondelete="CASCADE"),
        nullable=False
    )

    title = db.Column(db.UnicodeText, nullable=False)
    description = db.Column(db.UnicodeText)
    
    tipo = db.Column(db.String(64), default=TaskType.PRATICA.value)
    status = db.Column(db.String(64), default=MetaStatus.PENDING.value)
    dificuldade = db.Column(db.String(64), default=Dificuldade.MEDIA.value)
    
    # Planejamento
    pontos = db.Column(db.Integer, default=0)  # Pontos de complexidade
    tempo_estimado = db.Column(db.Integer)  # Em minutos
    recurso = db.Column(db.UnicodeText)  # Recursos necessários
    
    # Datas
    data_prevista = db.Column(db.DateTime, nullable=True)
    data_conclusao = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relacionamentos
    meta = db.relationship("Meta", back_populates="Tasks")
    pdi = db.relationship("PDI")

    def complete(self):
        """Marca Task como concluída"""
        self.status = MetaStatus.COMPLETED.value
        self.data_conclusao = datetime.now(timezone.utc)
        db.session.commit()
        
        # Propaga para a meta
        if self.meta:
            self.meta.update_progress()

    def __repr__(self):
        return f"<Task {self.id} - {self.title}>"
    
# ------------------------------
# Pydantic Schemas 
# ------------------------------

class TaskCreate(BaseModel):
    meta_id: int
    pdi_id: int
    title: str
    description: Optional[str] = None
    tipo: Optional[str] = TaskType.PRATICA.value
    dificuldade: Optional[str] = Dificuldade.MEDIA.value
    pontos: Optional[int] = 0
    tempo_estimado: Optional[int] = None
    recurso: Optional[str] = None
    data_prevista: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tipo: Optional[str] = None
    status: Optional[str] = None
    dificuldade: Optional[str] = None
    pontos: Optional[int] = None
    tempo_estimado: Optional[int] = None
    recurso: Optional[str] = None
    data_prevista: Optional[datetime] = None
    data_conclusao: Optional[datetime] = None


class TaskResponse(OrmBase):
    id: int
    meta_id: int
    pdi_id: int
    title: str
    description: Optional[str]
    tipo: str
    status: str
    dificuldade: str
    pontos: int
    tempo_estimado: Optional[int]
    recurso: Optional[str]
    
    # Datas
    data_prevista: Optional[datetime]
    data_conclusao: Optional[datetime]
    created_at: datetime

