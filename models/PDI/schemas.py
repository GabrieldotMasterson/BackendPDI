# models/PDI/schemas.py
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from .enums import PDIStatus, MetaStatus, TarefaTipo, Dificuldade, Prioridade, ProjetoTipo
from utils.models import OrmBase

class SmartCriteria(BaseModel):
    specific: Optional[str] = None
    measurable: Optional[str] = None
    achievable: Optional[str] = None
    relevant: Optional[str] = None
    time_bound: Optional[str] = None

# PDI Schemas
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


# Meta Schemas
class MetaCreate(BaseModel):
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


class MetaResponse(OrmBase):
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


# Tarefa Schemas
class TarefaCreate(BaseModel):
    meta_id: int
    pdi_id: int
    title: str
    description: Optional[str] = None
    tipo: Optional[str] = TarefaTipo.PRATICA.value
    dificuldade: Optional[str] = Dificuldade.MEDIA.value
    pontos: Optional[int] = 0
    tempo_estimado: Optional[int] = None
    recurso: Optional[str] = None
    data_prevista: Optional[datetime] = None


class TarefaResponse(OrmBase):
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


# Projeto Schemas
class ProjetoCreate(BaseModel):
    pdi_id: int
    title: str
    description: Optional[str] = None
    tipo: Optional[str] = ProjetoTipo.APLICACAO.value
    dificuldade: Optional[str] = Dificuldade.MEDIA.value
    horas_estimadas: Optional[int] = None
    data_inicio: Optional[datetime] = None
    data_fim_previsto: Optional[datetime] = None
    link: Optional[str] = None
    tecnologias: Optional[List[str]] = []


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


# Schemas de Resposta Completa
class PDIResponseCompleto(PDIResponse):
    metas: List[MetaResponse] = []
    projetos: List[ProjetoResponse] = []


class PDIResponseList(BaseModel):
    page: int
    pages: int
    total: int
    pdis: List[PDIResponse]