# controllers/PDIController.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from spectree import Response
import math

from app import db, api
from models.UserModel import User
from models.StudentModel import Student
from models.PDI import PDI, Meta, Tarefa, Projeto
from models.PDI.enums import PDIStatus, Prioridade
from models.PDI.schemas import (
    PDICreate, PDIUpdate, PDIResponse, PDIResponseCompleto,
    MetaCreate, MetaResponse,
    TarefaCreate, TarefaResponse,
    ProjetoCreate, ProjetoResponse,
    PDIResponseList
)
from datetime import datetime, timezone

# Importar ou definir esquema para respostas de erro
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """Schema para respostas de erro"""
    error: str

class MessageResponse(BaseModel):
    """Schema para respostas de mensagem"""
    message: str

# Cria o blueprint do PDI
pdi_bp = Blueprint('pdi', __name__, url_prefix='/pdi')

# ----------------------------
# Rotas PDI
# ----------------------------

@pdi_bp.route('/', methods=['POST'])
@jwt_required()
@api.validate(
    json=PDICreate,
    resp=Response(HTTP_201=PDIResponse, HTTP_404=ErrorResponse, HTTP_400=ErrorResponse),
    tags=["PDI"]
)
def create_pdi():
    """
    Criar um novo Plano de Desenvolvimento Individual (PDI)
    
    Cria um novo PDI para um estudante com metodologia SMART.
    Requer autenticação JWT.
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.context.json
        
        # Verificar se student_id é válido
        student = db.session.get(Student, data.student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        # Criar PDI
        new_pdi = PDI(
            title=data.title,
            subtitle=data.subtitle,
            description=data.description,
            goal=data.goal,
            student_id=data.student_id,
            mentor_id=data.mentor_id,
            category=data.category,
            nivel=data.nivel,
            priority=data.priority,
            deadline=data.deadline,
            data_inicio=data.data_inicio,
            is_specific=data.is_specific,
            is_measurable=data.is_measurable,
            is_achievable=data.is_achievable,
            is_relevant=data.is_relevant,
            is_time_bound=data.is_time_bound
        )
        
        db.session.add(new_pdi)
        db.session.commit()
        
        response = PDIResponse.model_validate(new_pdi).model_dump()
        return jsonify(response), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@pdi_bp.route('/', methods=['GET'])
@jwt_required()
@api.validate(
    resp=Response(HTTP_200=PDIResponseList, HTTP_400=ErrorResponse),
    tags=["PDI"]
)
def get_all_pdis():
    """
    Listar todos os PDIs
    
    Retorna uma lista paginada de PDIs.
    Pode filtrar por status e student_id.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        student_id = request.args.get('student_id')
        
        # Construir query
        query = PDI.query
        
        if status:
            query = query.filter(PDI.status == status)
        if student_id:
            query = query.filter(PDI.student_id == student_id)
        
        # Paginação
        total = query.count()
        pages = math.ceil(total / per_page) if total > 0 else 1
        pdis = query.order_by(PDI.created_at.desc())\
                   .offset((page - 1) * per_page)\
                   .limit(per_page)\
                   .all()
        
        response = PDIResponseList(
            page=page,
            pages=pages,
            total=total,
            pdis=[PDIResponse.model_validate(pdi).model_dump() for pdi in pdis]
        ).model_dump()
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@pdi_bp.route('/<int:pdi_id>', methods=['GET'])
@jwt_required()
@api.validate(
    resp=Response(HTTP_200=PDIResponseCompleto, HTTP_404=ErrorResponse),
    tags=["PDI"]
)
def get_one_pdi(pdi_id):
    """
    Obter um PDI específico
    
    Retorna os detalhes completos de um PDI, incluindo metas e projetos.
    """
    try:
        pdi = db.session.get(PDI, pdi_id)
        if not pdi:
            return jsonify({"error": f"PDI {pdi_id} not found"}), 404
        
        # Carregar metas e projetos
        metas = Meta.query.filter_by(pdi_id=pdi_id).all()
        projetos = Projeto.query.filter_by(pdi_id=pdi_id).all()
        
        pdi_response = PDIResponseCompleto(
            **PDIResponse.model_validate(pdi).model_dump(),
            metas=[MetaResponse.model_validate(meta).model_dump() for meta in metas],
            projetos=[ProjetoResponse.model_validate(projeto).model_dump() for projeto in projetos]
        ).model_dump()
        
        return jsonify(pdi_response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@pdi_bp.route('/<int:pdi_id>', methods=['PUT'])
@jwt_required()
@api.validate(
    json=PDIUpdate,
    resp=Response(HTTP_200=PDIResponse, HTTP_404=ErrorResponse, HTTP_400=ErrorResponse),
    tags=["PDI"]
)
def update_pdi(pdi_id):
    """
    Atualizar um PDI
    
    Atualiza os dados de um PDI existente.
    """
    try:
        pdi = db.session.get(PDI, pdi_id)
        if not pdi:
            return jsonify({"error": f"PDI {pdi_id} not found"}), 404
        
        data = request.context.json
        
        # Atualizar campos
        for field, value in data.dict(exclude_unset=True).items():
            if value is not None:
                setattr(pdi, field, value)
        
        pdi.last_update = datetime.now(timezone.utc)
        db.session.commit()
        
        response = PDIResponse.model_validate(pdi).model_dump()
        return jsonify(response), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@pdi_bp.route('/<int:pdi_id>', methods=['DELETE'])
@jwt_required()
@api.validate(
    resp=Response(HTTP_200=MessageResponse, HTTP_404=ErrorResponse, HTTP_400=ErrorResponse),
    tags=["PDI"]
)
def delete_pdi(pdi_id):
    """
    Deletar um PDI
    
    Remove permanentemente um PDI e todos os seus dados relacionados.
    """
    try:
        pdi = db.session.get(PDI, pdi_id)
        if not pdi:
            return jsonify({"error": f"PDI {pdi_id} not found"}), 404
        
        db.session.delete(pdi)
        db.session.commit()
        
        return jsonify({"message": "PDI deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# ----------------------------
# Rotas para Metas
# ----------------------------

@pdi_bp.route('/<int:pdi_id>/metas', methods=['GET'])
@jwt_required()
@api.validate(
    resp=Response(HTTP_200=MetaResponse(many=True), HTTP_400=ErrorResponse),
    tags=["Metas"]
)
def get_metas(pdi_id):
    """
    Listar metas de um PDI
    
    Retorna todas as metas associadas a um PDI específico.
    """
    try:
        metas = Meta.query.filter_by(pdi_id=pdi_id).order_by(Meta.ordem).all()
        
        # Adicionar contagem de tarefas
        metas_response = []
        for meta in metas:
            meta_data = MetaResponse.model_validate(meta).model_dump()
            meta_data['tarefas_concluidas'] = len([t for t in meta.tarefas if t.status == "completed"])
            meta_data['tarefas_totais'] = len(meta.tarefas)
            metas_response.append(meta_data)
        
        return jsonify(metas_response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@pdi_bp.route('/<int:pdi_id>/metas', methods=['POST'])
@jwt_required()
@api.validate(
    json=MetaCreate,
    resp=Response(HTTP_201=MetaResponse, HTTP_404=ErrorResponse, HTTP_400=ErrorResponse),
    tags=["Metas"]
)
def create_meta(pdi_id):
    """
    Criar uma meta para um PDI
    
    Adiciona uma nova meta SMART a um PDI existente.
    """
    try:
        pdi = db.session.get(PDI, pdi_id)
        if not pdi:
            return jsonify({"error": f"PDI {pdi_id} not found"}), 404
        
        data = request.context.json
        
        new_meta = Meta(
            pdi_id=pdi_id,
            title=data.title,
            description=data.description,
            specific=data.specific,
            measurable=data.measurable,
            achievable=data.achievable,
            relevant=data.relevant,
            time_bound=data.time_bound,
            peso=data.peso,
            ordem=data.ordem,
            data_inicio=data.data_inicio,
            data_fim_previsto=data.data_fim_previsto,
            evidencia_requisito=data.evidencia_requisito
        )
        
        db.session.add(new_meta)
        db.session.commit()
        
        # Atualizar progresso do PDI
        pdi.update_progress()
        
        response = MetaResponse.model_validate(new_meta).model_dump()
        return jsonify(response), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# ----------------------------
# Rotas para Tarefas
# ----------------------------

@pdi_bp.route('/metas/<int:meta_id>/tarefas', methods=['GET'])
@jwt_required()
@api.validate(
    resp=Response(HTTP_200=TarefaResponse(many=True), HTTP_400=ErrorResponse),
    tags=["Tarefas"]
)
def get_tarefas(meta_id):
    """
    Listar tarefas de uma meta
    
    Retorna todas as tarefas associadas a uma meta específica.
    """
    try:
        tarefas = Tarefa.query.filter_by(meta_id=meta_id).order_by(Tarefa.created_at).all()
        
        response = [TarefaResponse.model_validate(tarefa).model_dump() for tarefa in tarefas]
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@pdi_bp.route('/metas/<int:meta_id>/tarefas', methods=['POST'])
@jwt_required()
@api.validate(
    json=TarefaCreate,
    resp=Response(HTTP_201=TarefaResponse, HTTP_404=ErrorResponse, HTTP_400=ErrorResponse),
    tags=["Tarefas"]
)
def create_tarefa(meta_id):
    """
    Criar uma tarefa para uma meta
    
    Adiciona uma nova tarefa a uma meta existente.
    """
    try:
        meta = db.session.get(Meta, meta_id)
        if not meta:
            return jsonify({"error": f"Meta {meta_id} not found"}), 404
        
        data = request.context.json
        
        new_tarefa = Tarefa(
            meta_id=meta_id,
            pdi_id=meta.pdi_id,
            title=data.title,
            description=data.description,
            tipo=data.tipo,
            dificuldade=data.dificuldade,
            pontos=data.pontos,
            tempo_estimado=data.tempo_estimado,
            recurso=data.recurso,
            data_prevista=data.data_prevista
        )
        
        db.session.add(new_tarefa)
        db.session.commit()
        
        # Atualizar progresso da meta e PDI
        meta.update_progress()
        
        response = TarefaResponse.model_validate(new_tarefa).model_dump()
        return jsonify(response), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@pdi_bp.route('/tarefas/<int:tarefa_id>/complete', methods=['PUT'])
@jwt_required()
@api.validate(
    resp=Response(HTTP_200=TarefaResponse, HTTP_404=ErrorResponse, HTTP_400=ErrorResponse),
    tags=["Tarefas"]
)
def complete_tarefa(tarefa_id):
    """
    Marcar tarefa como concluída
    
    Atualiza o status de uma tarefa para "concluída" e propaga o progresso.
    """
    try:
        tarefa = db.session.get(Tarefa, tarefa_id)
        if not tarefa:
            return jsonify({"error": f"Tarefa {tarefa_id} not found"}), 404
        
        tarefa.complete()
        
        response = TarefaResponse.model_validate(tarefa).model_dump()
        return jsonify(response), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# ----------------------------
# Rotas para Projetos
# ----------------------------

@pdi_bp.route('/<int:pdi_id>/projetos', methods=['GET'])
@jwt_required()
@api.validate(
    resp=Response(HTTP_200=ProjetoResponse(many=True), HTTP_400=ErrorResponse),
    tags=["Projetos"]
)
def get_projetos(pdi_id):
    """
    Listar projetos de um PDI
    
    Retorna todos os projetos associados a um PDI específico.
    """
    try:
        projetos = Projeto.query.filter_by(pdi_id=pdi_id).order_by(Projeto.created_at).all()
        
        response = [ProjetoResponse.model_validate(projeto).model_dump() for projeto in projetos]
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@pdi_bp.route('/<int:pdi_id>/projetos', methods=['POST'])
@jwt_required()
@api.validate(
    json=ProjetoCreate,
    resp=Response(HTTP_201=ProjetoResponse, HTTP_404=ErrorResponse, HTTP_400=ErrorResponse),
    tags=["Projetos"]
)
def create_projeto(pdi_id):
    """
    Criar um projeto para um PDI
    
    Adiciona um novo projeto a um PDI existente.
    """
    try:
        pdi = db.session.get(PDI, pdi_id)
        if not pdi:
            return jsonify({"error": f"PDI {pdi_id} not found"}), 404
        
        data = request.context.json
        
        new_projeto = Projeto(
            pdi_id=pdi_id,
            title=data.title,
            description=data.description,
            tipo=data.tipo,
            dificuldade=data.dificuldade,
            horas_estimadas=data.horas_estimadas,
            data_inicio=data.data_inicio,
            data_fim_previsto=data.data_fim_previsto,
            link=data.link,
            tecnologias=data.tecnologias or []
        )
        
        db.session.add(new_projeto)
        db.session.commit()
        
        response = ProjetoResponse.model_validate(new_projeto).model_dump()
        return jsonify(response), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# ----------------------------
# Rotas adicionais úteis
# ----------------------------

@pdi_bp.route('/students/<int:student_id>', methods=['GET'])
@jwt_required()
@api.validate(
    resp=Response(HTTP_200=PDIResponseList, HTTP_400=ErrorResponse),
    tags=["PDI"]
)
def get_pdis_by_student(student_id):
    """
    Listar PDIs de um estudante específico
    
    Retorna todos os PDIs associados a um estudante.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pdis = PDI.query.filter_by(student_id=student_id)\
                       .order_by(PDI.created_at.desc())\
                       .paginate(page=page, per_page=per_page, error_out=False)
        
        response = PDIResponseList(
            page=pdis.page,
            pages=pdis.pages,
            total=pdis.total,
            pdis=[PDIResponse.model_validate(pdi).model_dump() for pdi in pdis.items]
        ).model_dump()
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@pdi_bp.route('/me', methods=['GET'])
@jwt_required()
@api.validate(
    resp=Response(HTTP_200=PDIResponseList, HTTP_404=ErrorResponse, HTTP_400=ErrorResponse),
    tags=["PDI"]
)
def get_my_pdis():
    """
    Listar PDIs do usuário atual
    
    Retorna todos os PDIs do estudante associado ao usuário autenticado.
    """
    try:
        current_user_id = get_jwt_identity()
        
        student = Student.query.filter_by(user_id=current_user_id).first()
        if not student:
            return jsonify({"error": "Student profile not found"}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pdis = PDI.query.filter_by(student_id=student.id)\
                       .order_by(PDI.created_at.desc())\
                       .paginate(page=page, per_page=per_page, error_out=False)
        
        response = PDIResponseList(
            page=pdis.page,
            pages=pdis.pages,
            total=pdis.total,
            pdis=[PDIResponse.model_validate(pdi).model_dump() for pdi in pdis.items]
        ).model_dump()
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400