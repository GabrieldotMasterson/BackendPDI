# routes.py
from flask import Blueprint
from controllers import (
    AuthController, UserController, StudentController,
    TeacherController, PDIController
)

# Criar blueprint para PDI
pdi_bp = Blueprint('pdi', __name__)

# Rotas PDI
pdi_bp.route('/pdi', methods=['POST'])(PDIController.create)
pdi_bp.route('/pdi', methods=['GET'])(PDIController.get_all)
pdi_bp.route('/pdi/<int:pdi_id>', methods=['GET'])(PDIController.get_one)
pdi_bp.route('/pdi/<int:pdi_id>', methods=['PUT'])(PDIController.update)
pdi_bp.route('/pdi/<int:pdi_id>', methods=['DELETE'])(PDIController.delete)

# Rotas para Metas
pdi_bp.route('/pdi/<int:pdi_id>/metas', methods=['GET'])(PDIController.get_metas)
pdi_bp.route('/pdi/<int:pdi_id>/metas', methods=['POST'])(PDIController.create_meta)

# Rotas para Tarefas
pdi_bp.route('/metas/<int:meta_id>/tarefas', methods=['GET'])(PDIController.get_tarefas)
pdi_bp.route('/metas/<int:meta_id>/tarefas', methods=['POST'])(PDIController.create_tarefa)
pdi_bp.route('/tarefas/<int:tarefa_id>/complete', methods=['PUT'])(PDIController.complete_tarefa)

# Rotas para Projetos
pdi_bp.route('/pdi/<int:pdi_id>/projetos', methods=['GET'])(PDIController.get_projetos)
pdi_bp.route('/pdi/<int:pdi_id>/projetos', methods=['POST'])(PDIController.create_projeto)

def register_routes(app):
    """Registra todos os blueprints na aplicação"""
    
    # Registrar blueprints existentes
    app.register_blueprint(AuthController.auth_bp, url_prefix='/api/auth')
    app.register_blueprint(UserController.user_bp, url_prefix='/api/users')
    app.register_blueprint(StudentController.student_bp, url_prefix='/api/students')
    app.register_blueprint(TeacherController.teacher_bp, url_prefix='/api/teachers')
    
    # Registrar blueprint PDI
    app.register_blueprint(pdi_bp, url_prefix='/api')
    
    return app