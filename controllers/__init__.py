# controllers/__init__.py
from .auth import auth_bp
from .user import user_bp
from .PDIController import pdi_bp 

__all__ = ['auth_bp', 'user_bp', 'pdi_bp']