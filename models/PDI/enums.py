# models/PDI/enums.py
from enum import Enum

class PDIStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class MetaStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TarefaTipo(str, Enum):
    ESTUDO = "estudo"
    PRATICA = "pratica"
    ANALISE = "analise"
    DESENVOLVIMENTO = "desenvolvimento"
    REVISAO = "revisao"


class Dificuldade(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"


class Prioridade(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"


class ProjetoTipo(str, Enum):
    VIDEO = "video"
    APLICACAO = "aplicacao"
    BIBLIOTECA = "biblioteca"
    EVENTO = "evento"
    DOCUMENTACAO = "documentacao"
    PESQUISA = "pesquisa"