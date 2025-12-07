# models/__init__.py
from .UserModel import User
from .StudentModel import Student

# Importar modelos PDI
from .PDI.pdi_model import PDI
from .PDI.meta_model import Meta
from .PDI.tarefa_model import Tarefa
from .PDI.projeto_model import Projeto

__all__ = ['User', 'Student', 'Teacher', 'PDI', 'Meta', 'Tarefa', 'Projeto']