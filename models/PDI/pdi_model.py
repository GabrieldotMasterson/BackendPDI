# models/PDI/pdi_model.py
from datetime import datetime, timezone
from app import db
from .enums import PDIStatus, Prioridade

class PDI(db.Model):
    __tablename__ = "pdi"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.UnicodeText, nullable=False)
    subtitle = db.Column(db.UnicodeText)
    description = db.Column(db.UnicodeText)
    goal = db.Column(db.UnicodeText) 

    status = db.Column(db.String(64), default=PDIStatus.OPEN.value)  
    progress = db.Column(db.Integer, default=0)

    # Campos SMART
    is_specific = db.Column(db.Boolean, default=False)
    is_measurable = db.Column(db.Boolean, default=False)
    is_achievable = db.Column(db.Boolean, default=False)
    is_relevant = db.Column(db.Boolean, default=False)
    is_time_bound = db.Column(db.Boolean, default=False)

    # Categorização
    category = db.Column(db.String(128))
    priority = db.Column(db.String(64), default=Prioridade.MEDIA.value)
    nivel = db.Column(db.String(64))

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

    # NOTA: Os relacionamentos serão configurados no __init__.py

    @property
    def metas_concluidas(self):
        if hasattr(self, 'metas'):
            metas = self.metas.all() if hasattr(self.metas, 'all') else self.metas
            return len([m for m in metas if m.status == "completed"])
        return 0
    
    @property
    def metas_totais(self):
        if hasattr(self, 'metas'):
            metas = self.metas.all() if hasattr(self.metas, 'all') else self.metas
            return len(metas)
        return 0
    
    @property
    def projetos_concluidos(self):
        if hasattr(self, 'projetos'):
            projetos = self.projetos.all() if hasattr(self.projetos, 'all') else self.projetos
            return len([p for p in projetos if p.status == "completed"])
        return 0
    
    @property
    def projetos_totais(self):
        if hasattr(self, 'projetos'):
            projetos = self.projetos.all() if hasattr(self.projetos, 'all') else self.projetos
            return len(projetos)
        return 0

    def update_progress(self):
        """Atualiza progresso automaticamente baseado nas metas"""
        from .meta_model import Meta
        
        metas = Meta.query.filter_by(pdi_id=self.id).all()
        if not metas:
            self.progress = 0
            db.session.commit()
            return
        
        total_peso = sum(meta.peso for meta in metas if meta.peso)
        if total_peso == 0:
            progressos = [meta.progress for meta in metas]
            self.progress = sum(progressos) // len(progressos) if progressos else 0
        else:
            weighted_sum = sum(meta.progress * meta.peso for meta in metas if meta.peso)
            self.progress = weighted_sum // total_peso
        
        if self.progress == 100:
            self.status = PDIStatus.COMPLETED.value
        elif self.progress > 0:
            self.status = PDIStatus.IN_PROGRESS.value
        
        self.last_update = datetime.now(timezone.utc)
        db.session.commit()

    def __repr__(self):
        return f"<PDI {self.id} - {self.title}>"