# models/PDI/projeto_model.py
from datetime import datetime, timezone
from factory import db
from .enums import MetaStatus, Dificuldade, ProjetoTipo

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
    
    tipo = db.Column(db.String(128), default=ProjetoTipo.APLICACAO.value)
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
    tecnologias = db.Column(db.JSON, default=list)
    
    # NOTA: Os relacionamentos serão configurados no __init__.py

    @property
    def entregaveis(self):
        # Pode ser estendido para buscar de uma tabela separada
        return []

    def __repr__(self):
        return f"<Projeto {self.id} - {self.title}>"