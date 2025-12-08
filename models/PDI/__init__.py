# models/PDI/__init__.py
# Este arquivo configura os relacionamentos após todos os modelos serem importados
from app import db
from .enums import *
from .pdi_model import PDI
from .meta_model import Meta
from .tarefa_model import Tarefa
from .projeto_model import Projeto

# Configurar relacionamentos
PDI.metas = db.relationship("Meta", back_populates="pdi", cascade="all, delete-orphan", lazy="dynamic")
PDI.projetos = db.relationship("Projeto", back_populates="pdi", cascade="all, delete-orphan", lazy="dynamic")

Meta.pdi = db.relationship("PDI", back_populates="metas")
Meta.tarefas = db.relationship("Tarefa", back_populates="meta", cascade="all, delete-orphan", lazy="dynamic")

Tarefa.meta = db.relationship("Meta", back_populates="tarefas")
Tarefa.pdi = db.relationship("PDI", foreign_keys=[Tarefa.pdi_id])

Projeto.pdi = db.relationship("PDI", back_populates="projetos")

__all__ = [
    'PDI', 'Meta', 'Tarefa', 'Projeto',
    'PDIStatus', 'MetaStatus', 'TarefaTipo', 'Dificuldade', 'Prioridade', 'ProjetoTipo'
]