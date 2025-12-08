# models/PDI/meta_model.py
from datetime import datetime, timezone
from app import db
from .enums import MetaStatus

class Meta(db.Model):
    __tablename__ = "pdi_metas"

    id = db.Column(db.Integer, primary_key=True)

    pdi_id = db.Column(
        db.Integer,
        db.ForeignKey("pdi.id", ondelete="CASCADE"),
        nullable=False
    )

    title = db.Column(db.UnicodeText, nullable=False)
    description = db.Column(db.UnicodeText)
    
    # Campos SMART detalhados
    specific = db.Column(db.UnicodeText)
    measurable = db.Column(db.UnicodeText)
    achievable = db.Column(db.UnicodeText)
    relevant = db.Column(db.UnicodeText)
    time_bound = db.Column(db.UnicodeText)
    
    status = db.Column(db.String(64), default=MetaStatus.PENDING.value)
    progress = db.Column(db.Integer, default=0)
    
    # Planejamento
    peso = db.Column(db.Integer, default=0)
    ordem = db.Column(db.Integer, default=0)
    
    # Datas
    data_inicio = db.Column(db.DateTime, nullable=True)
    data_fim_previsto = db.Column(db.DateTime, nullable=True)
    data_fim = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Evidências
    evidencia_requisito = db.Column(db.UnicodeText)
    
    # NOTA: Os relacionamentos serão configurados no __init__.py

    def update_progress(self):
        """Atualiza progresso baseado nas tarefas"""
        from .tarefa_model import Tarefa
        
        tarefas = Tarefa.query.filter_by(meta_id=self.id).all()
        if not tarefas:
            self.progress = 0
            db.session.commit()
            return
        
        concluidas = len([t for t in tarefas if t.status == "completed"])
        total = len(tarefas)
        self.progress = (concluidas * 100) // total if total > 0 else 0
        
        if self.progress == 100:
            self.status = MetaStatus.COMPLETED.value
            self.data_fim = datetime.now(timezone.utc)
        elif self.progress > 0:
            self.status = MetaStatus.IN_PROGRESS.value
        
        db.session.commit()
        # Propaga para o PDI
        from .pdi_model import PDI
        pdi = PDI.query.get(self.pdi_id)
        if pdi:
            pdi.update_progress()

    def __repr__(self):
        return f"<Meta {self.id} - {self.title}>"