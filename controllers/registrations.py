from factory import db, api
from sqlalchemy import select
from flask import Blueprint, request
from spectree import response
from pydantic import BaseModel
from flask_jwt_extended import current_user, jwt_required
from datetime import datetime

from models.registrations import RegisterUserInTalk, UnregisterUserInTalk, RegistrationsResponses, Registrations
from models.PDIModel import Talks

registration_controller = Blueprint("registration_controller", __name__, url_prefix="/registration")

@registration_controller.post("/<talk_id>/register")
@jwt_required()
@api.validate(tags=["registrations"])
def register_user_in_talk(talk_id):
    user = current_user
    talk = db.session.get(Talks, talk_id)
    if not talk:
        return {"msg": "Não encontramos essa tabela :("}, 404
    
    exists = db.session.scalar(
        select(Registrations).where(
            Registrations.user_id == user.id,
            Registrations.talk_id == talk_id
        )
    )

    if exists:
        return {"msg": "Usuario já registrado na palestra"}, 400
    
    db.session.add(Registrations(user_id=user.id, talk_id=talk_id))
    db.session.commit()

    return {"msg": "Registrado!"}, 201

@registration_controller.post("/<talk_id>/unregister")
@jwt_required()
@api.validate(tags=["registrations"])
def unregister_user_in_talk(talk_id):
    user =current_user

    registration = db.session.scalar(
        select(Registrations).where(
            Registrations.user_id == user.id,
            Registrations.talk_id == talk_id
        )
    )
    if not registration:
        return {"msg": "O usuario não estava registrado"}, 400
    
    db.session.delete(registration)
    db.session.commit()
    return {"msg": "inscrição cancelada"}, 200

@registration_controller.get("/<talk_id>/is_registered")
@jwt_required()
@api.validate(tags=["registrations"])
def is_registered(talk_id):
    user = current_user
    exists = db.session.scalar(
        select(Registrations).where(
            Registrations.user_id == user.id,
            Registrations.talk_id == talk_id
        )
    )
    return {"registered": bool(exists) }, 200

