# controllers/PDIController.py
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
import math

from factory import db
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

class PDIController:
    
    @staticmethod
    @jwt_required()
    def create():
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            # Validar dados com Pydantic
            pdi_data = PDICreate(**data)
            
            # Verificar se student_id é válido
            student = Student.query.get(pdi_data.student_id)
            if not student:
                return jsonify({"error": "Student not found"}), 404
            
            # Criar PDI
            new_pdi = PDI(
                title=pdi_data.title,
                subtitle=pdi_data.subtitle,
                description=pdi_data.description,
                goal=pdi_data.goal,
                student_id=pdi_data.student_id,
                mentor_id=pdi_data.mentor_id,
                category=pdi_data.category,
                nivel=pdi_data.nivel,
                priority=pdi_data.priority,
                deadline=pdi_data.deadline,
                data_inicio=pdi_data.data_inicio,
                is_specific=pdi_data.is_specific,
                is_measurable=pdi_data.is_measurable,
                is_achievable=pdi_data.is_achievable,
                is_relevant=pdi_data.is_relevant,
                is_time_bound=pdi_data.is_time_bound
            )
            
            db.session.add(new_pdi)
            db.session.commit()
            
            return jsonify(PDIResponse.from_orm(new_pdi).dict()), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400
    
    @staticmethod
    @jwt_required()
    def get_all():
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
                pdis=[PDIResponse.from_orm(pdi) for pdi in pdis]
            )
            
            return jsonify(response.dict()), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    @staticmethod
    @jwt_required()
    def get_one(pdi_id):
        try:
            pdi = PDI.query.get_or_404(pdi_id)
            
            # Carregar metas e projetos
            metas = Meta.query.filter_by(pdi_id=pdi_id).all()
            projetos = Projeto.query.filter_by(pdi_id=pdi_id).all()
            
            pdi_response = PDIResponse.from_orm(pdi)
            response_data = pdi_response.dict()
            response_data['metas'] = [MetaResponse.from_orm(meta).dict() for meta in metas]
            response_data['projetos'] = [ProjetoResponse.from_orm(projeto).dict() for projeto in projetos]
            
            return jsonify(response_data), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    @staticmethod
    @jwt_required()
    def update(pdi_id):
        try:
            pdi = PDI.query.get_or_404(pdi_id)
            data = request.get_json()
            
            # Validar dados
            update_data = PDIUpdate(**data)
            
            # Atualizar campos
            for field, value in update_data.dict(exclude_unset=True).items():
                if value is not None:
                    setattr(pdi, field, value)
            
            pdi.last_update = datetime.now(timezone.utc)
            db.session.commit()
            
            return jsonify(PDIResponse.from_orm(pdi).dict()), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400
    
    @staticmethod
    @jwt_required()
    def delete(pdi_id):
        try:
            pdi = PDI.query.get_or_404(pdi_id)
            
            db.session.delete(pdi)
            db.session.commit()
            
            return jsonify({"message": "PDI deleted successfully"}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400
    
    # Métodos para Metas
    @staticmethod
    @jwt_required()
    def create_meta(pdi_id):
        try:
            pdi = PDI.query.get_or_404(pdi_id)
            data = request.get_json()
            
            meta_data = MetaCreate(pdi_id=pdi_id, **data)
            
            new_meta = Meta(
                pdi_id=pdi_id,
                title=meta_data.title,
                description=meta_data.description,
                specific=meta_data.specific,
                measurable=meta_data.measurable,
                achievable=meta_data.achievable,
                relevant=meta_data.relevant,
                time_bound=meta_data.time_bound,
                peso=meta_data.peso,
                ordem=meta_data.ordem,
                data_inicio=meta_data.data_inicio,
                data_fim_previsto=meta_data.data_fim_previsto,
                evidencia_requisito=meta_data.evidencia_requisito
            )
            
            db.session.add(new_meta)
            db.session.commit()
            
            # Atualizar progresso do PDI
            pdi.update_progress()
            
            return jsonify(MetaResponse.from_orm(new_meta).dict()), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400
    
    @staticmethod
    @jwt_required()
    def get_metas(pdi_id):
        try:
            metas = Meta.query.filter_by(pdi_id=pdi_id).order_by(Meta.ordem).all()
            
            # Adicionar contagem de tarefas
            metas_response = []
            for meta in metas:
                meta_data = MetaResponse.from_orm(meta).dict()
                meta_data['tarefas_concluidas'] = len([t for t in meta.tarefas if t.status == "completed"])
                meta_data['tarefas_totais'] = len(meta.tarefas)
                metas_response.append(meta_data)
            
            return jsonify(metas_response), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    # Métodos para Tarefas
    @staticmethod
    @jwt_required()
    def create_tarefa(meta_id):
        try:
            meta = Meta.query.get_or_404(meta_id)
            data = request.get_json()
            
            tarefa_data = TarefaCreate(meta_id=meta_id, pdi_id=meta.pdi_id, **data)
            
            new_tarefa = Tarefa(
                meta_id=meta_id,
                pdi_id=meta.pdi_id,
                title=tarefa_data.title,
                description=tarefa_data.description,
                tipo=tarefa_data.tipo,
                dificuldade=tarefa_data.dificuldade,
                pontos=tarefa_data.pontos,
                tempo_estimado=tarefa_data.tempo_estimado,
                recurso=tarefa_data.recurso,
                data_prevista=tarefa_data.data_prevista
            )
            
            db.session.add(new_tarefa)
            db.session.commit()
            
            # Atualizar progresso da meta e PDI
            meta.update_progress()
            
            return jsonify(TarefaResponse.from_orm(new_tarefa).dict()), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400
    
    @staticmethod
    @jwt_required()
    def get_tarefas(meta_id):
        try:
            tarefas = Tarefa.query.filter_by(meta_id=meta_id).order_by(Tarefa.created_at).all()
            
            return jsonify([TarefaResponse.from_orm(tarefa).dict() for tarefa in tarefas]), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    # Métodos para Projetos
    @staticmethod
    @jwt_required()
    def create_projeto(pdi_id):
        try:
            pdi = PDI.query.get_or_404(pdi_id)
            data = request.get_json()
            
            projeto_data = ProjetoCreate(pdi_id=pdi_id, **data)
            
            new_projeto = Projeto(
                pdi_id=pdi_id,
                title=projeto_data.title,
                description=projeto_data.description,
                tipo=projeto_data.tipo,
                dificuldade=projeto_data.dificuldade,
                horas_estimadas=projeto_data.horas_estimadas,
                data_inicio=projeto_data.data_inicio,
                data_fim_previsto=projeto_data.data_fim_previsto,
                link=projeto_data.link,
                tecnologias=projeto_data.tecnologias or []
            )
            
            db.session.add(new_projeto)
            db.session.commit()
            
            return jsonify(ProjetoResponse.from_orm(new_projeto).dict()), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400
    
    @staticmethod
    @jwt_required()
    def get_projetos(pdi_id):
        try:
            projetos = Projeto.query.filter_by(pdi_id=pdi_id).order_by(Projeto.created_at).all()
            
            return jsonify([ProjetoResponse.from_orm(projeto).dict() for projeto in projetos]), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    # Método para completar tarefa
    @staticmethod
    @jwt_required()
    def complete_tarefa(tarefa_id):
        try:
            tarefa = Tarefa.query.get_or_404(tarefa_id)
            tarefa.complete()
            
            return jsonify(TarefaResponse.from_orm(tarefa).dict()), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400