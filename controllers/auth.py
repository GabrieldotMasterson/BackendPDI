from app import db, api

from sqlalchemy import select
from pydantic import BaseModel
from spectree import Response

from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required

from models import User
from utils.responses import DefaultResponse
from models.auth import LoginMessage,LoginResponseMessage


auth_controller = Blueprint("auth_controller", __name__, url_prefix="/auth")

@auth_controller.post("/login")
@api.validate(
    json=LoginMessage,
    resp=Response(HTTP_200=LoginResponseMessage, HTTP_401=DefaultResponse),
    security={},
    tags=["auth"],
)
def login():
    data = request.json
    print("data recebida no login:", data)

    user = db.session.scalars(select(User).filter_by(username=data["username"])).first()
    print("user:", user)
    print("senha correta?:", user.verify_password(data["password"]) if user else None)

    if user and user.verify_password(data["password"]):
        return {
            "access_token": create_access_token(
                identity=user.username, expires_delta=None
            )
        }

    return {"msg": "Senha ou nome errado"}, 401


@auth_controller.post("/logout")
@api.validate(resp=Response(HTTP_200=DefaultResponse), tags=["auth"])
@jwt_required()
def logout():
    return {"msg": "Entrou com sucesso"}
