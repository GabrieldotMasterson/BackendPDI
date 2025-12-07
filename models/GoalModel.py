from datetime import datetime, timezone
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

from factory import db
from utils.models import OrmBase
from models.UserModel import UserResponseSimple

class GoalStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Goal(db.Model):
    __tablename__ = "pdi_goals"

    id = db.Column(db.Integer, primary_key=True)

    pdi_id = db.Column(
        db.Integer,
        db.ForeignKey("pdi.id", ondelete="CASCADE"),
        nullable=False
    )

    title = db.Column(db.UnicodeText, nullable=False)
    description = db.Column(db.UnicodeText)
    
    specific = db.Column(db.UnicodeText)      
    measurable = db.Column(db.UnicodeText)    
    achievable = db.Column(db.UnicodeText)    
    relevant = db.Column(db.UnicodeText)      
    time_bound = db.Column(db.UnicodeText)    
    
    status = db.Column(db.String(64), default=GoalStatus.PENDING.value)
    progress = db.Column(db.Integer, default=0)  # 0-100
    
    peso = db.Column(db.Integer, default=0)  
    ordem = db.Column(db.Integer, default=0) 
    

    data_inicio = db.Column(db.DateTime, nullable=True)
    data_fim_previsto = db.Column(db.DateTime, nullable=True)
    data_fim = db.Column(db.DateTime, nullable=True)  
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    evidencia_requisito = db.Column(db.UnicodeText)  
    
    pdi = db.relationship("PDI", back_populates="Goals")
    tarefas = db.relationship("Tarefa", back_populates="Goal", cascade="all, delete-orphan")

    def update_progress(self):
        """Atualiza progresso baseado nas tarefas"""
        if not self.tarefas:
            self.progress = 0
            return
        
        concluidas = len([t for t in self.tarefas if t.status == GoalStatus.COMPLETED.value])
        total = len(self.tarefas)
        self.progress = (concluidas * 100) // total if total > 0 else 0
        
        # Atualiza status
        if self.progress == 100:
            self.status = MetaStatus.COMPLETED.value
            self.data_fim = datetime.now(timezone.utc)
        elif self.progress > 0:
            self.status = MetaStatus.IN_PROGRESS.value
        
        db.session.commit()
        # Propaga para o PDI
        if self.pdi:
            self.pdi.update_progress()

    def __repr__(self):
        return f"<Meta {self.id} - {self.title}>"


# ------------------------------
# Pydantic Schemas 
# ------------------------------

class GoalCreate(BaseModel):
    pdi_id: int
    title: str
    description: Optional[str] = None
    
    # SMART detalhado
    specific: Optional[str] = None
    measurable: Optional[str] = None
    achievable: Optional[str] = None
    relevant: Optional[str] = None
    time_bound: Optional[str] = None
    
    peso: Optional[int] = 0
    ordem: Optional[int] = 0
    data_inicio: Optional[datetime] = None
    data_fim_previsto: Optional[datetime] = None
    evidencia_requisito: Optional[str] = None


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    
    # SMART
    specific: Optional[str] = None
    measurable: Optional[str] = None
    achievable: Optional[str] = None
    relevant: Optional[str] = None
    time_bound: Optional[str] = None
    
    status: Optional[str] = None
    progress: Optional[int] = None
    peso: Optional[int] = None
    ordem: Optional[int] = None
    data_inicio: Optional[datetime] = None
    data_fim_previsto: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    evidencia_requisito: Optional[str] = None


class GoalResponse(OrmBase):
    id: int
    pdi_id: int
    title: str
    description: Optional[str]
    
    # SMART
    specific: Optional[str]
    measurable: Optional[str]
    achievable: Optional[str]
    relevant: Optional[str]
    time_bound: Optional[str]
    
    status: str
    progress: int
    peso: int
    ordem: int
    
    # Datas
    data_inicio: Optional[datetime]
    data_fim_previsto: Optional[datetime]
    data_fim: Optional[datetime]
    created_at: datetime
    evidencia_requisito: Optional[str]
    
    # Contagem de tarefas
    tarefas_concluidas: Optional[int] = 0
    tarefas_totais: Optional[int] = 0

