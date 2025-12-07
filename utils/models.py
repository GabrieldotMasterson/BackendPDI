# utils/models.py
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
import pytz

class OrmBase(BaseModel):
    """Base model that works with SQLAlchemy models"""
    
    class Config:
        from_attributes = True  # Substitui orm_mode no Pydantic v2
        json_encoders = {
            datetime: lambda dt: dt.astimezone(pytz.UTC).isoformat() if dt.tzinfo else dt.replace(tzinfo=pytz.UTC).isoformat()
        }
    
    @classmethod
    def from_orm(cls, obj: Any):
        """Alias para compatibility"""
        return cls.model_validate(obj)