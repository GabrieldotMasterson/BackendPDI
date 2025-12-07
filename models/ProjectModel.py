from datetime import datetime, timezone
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

from factory import db
from utils.models import OrmBase
from models.UserModel import UserResponseSimple

class Projeto(db.Model):
    __tablename__ = "pdi_projetos"

    id = db.Column(db.Integer, primary_key=True)

    pdi_id = db.Column(
        db.Integer,
        db.ForeignKey("pdi.id", ondelete="CASCADE"),
        nullable=False
    )

    title = db.Column(db.UnicodeText, nullable=False)
    description = db.Column(db.UnicodeText)
    
    tipo = db.Column(db.String(128))  # video, aplicacao, biblioteca, evento, etc.
    status = db.Column(db.String(64), default=MetaStatus.PENDING.value)
    progress = db.Column(db.Integer, default=0)
    
    dificuldade = db.Column(db.String(64), default=Dificuldade.MEDIA.value)
    horas_estimadas = db.Column(db.Integer)
    
    # Datas
    data_inicio = db.Column(db.DateTime, nullable=True)
    data_fim_previsto = db.Column(db.DateTime, nullable=True)
    data_fim = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Links e referências
    link = db.Column(db.String(512), nullable=True)
    tecnologias = db.Column(db.JSON, default=list)  # Lista de tecnologias
    
    # Relacionamentos
    pdi = db.relationship("PDI", back_populates="projetos")

    @property
    def entregaveis(self):
        # Pode ser armazenado como JSON ou texto estruturado
        # Por enquanto retorna lista vazia
        return []

    def __repr__(self):
        return f"<Projeto {self.id} - {self.title}>"
    



# ------------------------------
# Pydantic Schemas 
# ------------------------------

class ProjetoCreate(BaseModel):
    pdi_id: int
    title: str
    description: Optional[str] = None
    tipo: Optional[str] = None
    dificuldade: Optional[str] = Dificuldade.MEDIA.value
    horas_estimadas: Optional[int] = None
    data_inicio: Optional[datetime] = None
    data_fim_previsto: Optional[datetime] = None
    link: Optional[str] = None
    tecnologias: Optional[List[str]] = []


class ProjetoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tipo: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    dificuldade: Optional[str] = None
    horas_estimadas: Optional[int] = None
    data_inicio: Optional[datetime] = None
    data_fim_previsto: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    link: Optional[str] = None
    tecnologias: Optional[List[str]] = None


class ProjetoResponse(OrmBase):
    id: int
    pdi_id: int
    title: str
    description: Optional[str]
    tipo: Optional[str]
    status: str
    progress: int
    dificuldade: str
    horas_estimadas: Optional[int]
    
    # Datas
    data_inicio: Optional[datetime]
    data_fim_previsto: Optional[datetime]
    data_fim: Optional[datetime]
    created_at: datetime
    
    # Links e tecnologias
    link: Optional[str]
    tecnologias: List[str]
    entregaveis: List[str] = []


# ------------------------------
# Schemas para respostas completas
# ------------------------------

class PDIResponseCompleto(PDIResponse):
    metas: List[MetaResponse] = []
    projetos: List[ProjetoResponse] = []


class PDIResponseList(BaseModel):
    page: int
    pages: int
    total: int
    pdis: List[PDIResponse]
