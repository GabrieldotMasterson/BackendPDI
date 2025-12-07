# models/PDI/tarefa_model.py
from datetime import datetime, timezone
from factory import db
from .enums import MetaStatus, TarefaTipo, Dificuldade

class Tarefa(db.Model):
    __tablename__ = "pdi_tarefas"

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
    
    tipo = db.Column(db.String(64), default=TarefaTipo.PRATICA.value)
    status = db.Column(db.String(64), default=MetaStatus.PENDING.value)
    dificuldade = db.Column(db.String(64), default=Dificuldade.MEDIA.value)
    
    # Planejamento
    pontos = db.Column(db.Integer, default=0)
    tempo_estimado = db.Column(db.Integer)
    recurso = db.Column(db.UnicodeText)
    
    # Datas
    data_prevista = db.Column(db.DateTime, nullable=True)
    data_conclusao = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # NOTA: Os relacionamentos serão configurados no __init__.py

    def complete(self):
        """Marca tarefa como concluída"""
        self.status = MetaStatus.COMPLETED.value
        self.data_conclusao = datetime.now(timezone.utc)
        db.session.commit()
        
        # Propaga para a meta
        from .meta_model import Meta
        meta = Meta.query.get(self.meta_id)
        if meta:
            meta.update_progress()

    def __repr__(self):
        return f"<Tarefa {self.id} - {self.title}>"