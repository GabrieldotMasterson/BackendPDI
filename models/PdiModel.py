from datetime import datetime, timezone
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

from factory import db
from utils.models import OrmBase
from models.UserModel import UserResponseSimple


# ------------------------------
# Enums para consistência
# ------------------------------
class PDIStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Dificuldade(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"


class Prioridade(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"


# ------------------------------
# Tabela principal PDI
# ------------------------------
class PDI(db.Model):
    __tablename__ = "pdi"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.UnicodeText, nullable=False)
    subtitle = db.Column(db.UnicodeText)
    description = db.Column(db.UnicodeText)
    goal = db.Column(db.UnicodeText) 

    status = db.Column(db.String(64), default=PDIStatus.OPEN.value)  
    progress = db.Column(db.Integer, default=0)  # 0-100

    # Campos SMART
    is_specific = db.Column(db.Boolean, default=False)
    is_measurable = db.Column(db.Boolean, default=False)
    is_achievable = db.Column(db.Boolean, default=False)
    is_relevant = db.Column(db.Boolean, default=False)
    is_time_bound = db.Column(db.Boolean, default=False)

    # Categorização
    category = db.Column(db.String(128))
    priority = db.Column(db.String(64), default=Prioridade.MEDIA.value)
    nivel = db.Column(db.String(64))  # Iniciante, Intermediário, Avançado

    # Datas
    data_inicio = db.Column(db.DateTime, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_update = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id", ondelete="CASCADE"),
        nullable=False
    )
    mentor_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relacionamentos (backrefs)
    metas = db.relationship("Meta", back_populates="pdi", cascade="all, delete-orphan")
    projetos = db.relationship("Projeto", back_populates="pdi", cascade="all, delete-orphan")

    # Métricas calculadas (podem ser properties)
    @property
    def metas_concluidas(self):
        return len([m for m in self.metas if m.status == MetaStatus.COMPLETED.value])
    
    @property
    def metas_totais(self):
        return len(self.metas)
    
    @property
    def projetos_concluidos(self):
        return len([p for p in self.projetos if p.status == MetaStatus.COMPLETED.value])
    
    @property
    def projetos_totais(self):
        return len(self.projetos)

    def update_progress(self):
        """Atualiza progresso automaticamente baseado nas metas"""
        if not self.metas:
            self.progress = 0
            return
        
        total_peso = sum(meta.peso for meta in self.metas if meta.peso)
        if total_peso == 0:
            # Calcula média simples
            progressos = [meta.progress for meta in self.metas]
            self.progress = sum(progressos) // len(progressos) if progressos else 0
        else:
            # Calcula ponderado pelo peso
            weighted_sum = sum(meta.progress * meta.peso for meta in self.metas if meta.peso)
            self.progress = weighted_sum // total_peso
        
        # Atualiza status baseado no progresso
        if self.progress == 100:
            self.status = PDIStatus.COMPLETED.value
        elif self.progress > 0:
            self.status = PDIStatus.IN_PROGRESS.value
        
        db.session.commit()

    def __repr__(self):
        return f"<PDI {self.id} - {self.title}>"

# ------------------------------
# Pydantic Schemas para PDI
# ------------------------------

class SmartCriteria(BaseModel):
    specific: Optional[str] = None
    measurable: Optional[str] = None
    achievable: Optional[str] = None
    relevant: Optional[str] = None
    time_bound: Optional[str] = None


class PDICreate(BaseModel):
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    goal: Optional[str] = None
    category: Optional[str] = None
    nivel: Optional[str] = None
    priority: Optional[str] = Prioridade.MEDIA.value
    deadline: Optional[datetime] = None
    data_inicio: Optional[datetime] = None
    student_id: int
    mentor_id: Optional[int] = None
    
    # SMART
    is_specific: Optional[bool] = False
    is_measurable: Optional[bool] = False
    is_achievable: Optional[bool] = False
    is_relevant: Optional[bool] = False
    is_time_bound: Optional[bool] = False


class PDIUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    goal: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    nivel: Optional[str] = None
    deadline: Optional[datetime] = None
    last_update: Optional[datetime] = None
    
    # SMART
    is_specific: Optional[bool] = None
    is_measurable: Optional[bool] = None
    is_achievable: Optional[bool] = None
    is_relevant: Optional[bool] = None
    is_time_bound: Optional[bool] = None


class PDIResponse(OrmBase):
    id: int
    title: str
    subtitle: Optional[str]
    description: Optional[str]
    goal: Optional[str]
    status: str
    progress: int
    category: Optional[str]
    priority: Optional[str]
    nivel: Optional[str]
    
    # SMART
    is_specific: bool
    is_measurable: bool
    is_achievable: bool
    is_relevant: bool
    is_time_bound: bool
    
    # Datas
    data_inicio: Optional[datetime]
    deadline: Optional[datetime]
    created_at: datetime
    last_update: datetime
    
    # Relacionamentos
    student_id: int
    mentor_id: Optional[int]
    
    # Métricas calculadas
    metas_concluidas: int
    metas_totais: int
    projetos_concluidos: int
    projetos_totais: int
