from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy import select
from spectree import Response

from app import db, api
from models.UserModel import User, UserCreate, UserEdit, UserResponse, UserResponseList
from utils.responses import DefaultResponse


user_controller = Blueprint("user_controller", __name__, url_prefix="/users")


@user_controller.get("/me")
@jwt_required()
def me():
    response = UserResponse.model_validate(current_user).model_dump()

    return response, 200


@user_controller.get("/")
@api.validate(resp=Response(HTTP_200=UserResponseList), tags=["users"])
def get_users():

    users = db.session.scalars(select(User)).all()

    response = UserResponseList(
        users=[UserResponse.model_validate(user).model_dump() for user in users]
    ).model_dump()

    return response, 200


@user_controller.get("/<int:user_id>")
@api.validate(
    resp=Response(HTTP_200=UserResponse, HTTP_404=DefaultResponse), tags=["users"]
)
@jwt_required()
def get_user(user_id):
    if not (current_user and current_user.role.can_access_sensitive_information):
        return {
            "msg": "Você não tem permissão"
        }, 403

    user = db.session.get(User, user_id)
    if user is None:
        return {"msg": f"Usuário não encontrado {user_id}"}, 404

    response = UserResponse.model_validate(user).model_dump()

    return response, 200


@user_controller.post("/")
@api.validate(
    json=UserCreate,
    resp=Response(HTTP_201=DefaultResponse),
    security={},
    tags=["users"],
)
def post_user():
    data = request.json

    if db.session.scalars(select(User).filter_by(username=data["username"])).first():
        return {"msg": "username not available"}, 409

    if "birthdate" in data:
        if data["birthdate"].endswith("Z"):
            data["birthdate"] = data["birthdate"][:-1]
    user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        birthdate=(
            datetime.fromisoformat(data["birthdate"]) if "birthdate" in data else None
        ),
    )

    db.session.add(user)
    db.session.commit()

    return {"msg": "Usuário criado com sucesso"}, 201


@user_controller.put("/")
@api.validate(
    json=UserEdit,
    resp=Response(HTTP_200=DefaultResponse, HTTP_404=DefaultResponse),
    tags=["users"],
)
@jwt_required()
def put_user():
    user = current_user

    data = request.json

    user.username = data["username"]
    user.email = data["email"]

    if "birthdate" in data:
        if data["birthdate"].endswith("Z"):
            data["birthdate"] = data["birthdate"][:-1]
        user.birthdate = datetime.fromisoformat(data["birthdate"])

    if "password" in data:
        user.password = data["password"]


    db.session.commit()

    return {"msg": "Usuario foi modificado"}, 200


@user_controller.delete("/<int:user_id>")
@api.validate(
    resp=Response(HTTP_200=DefaultResponse, HTTP_404=DefaultResponse), tags=["users"]
)
@jwt_required()
def delete_user(user_id):
    if not (current_user and current_user.role.can_manage_users):
        return {"msg": "Você não tem permissão para deletar usuários"}, 403

    user = db.session.get(User, user_id)

    db.session.delete(user)
    db.session.commit()

    return {"msg": "Usuario foi deletado"}, 200

@user_controller.delete("/me")
@api.validate(
    resp=Response(HTTP_200=DefaultResponse, HTTP_404=DefaultResponse), tags=["users"]
)
@jwt_required()
def delete():
    user = db.session.get(User, current_user.id)

    db.session.delete(user)
    db.session.commit()

    return {"msg": "Usuario foi deletado"}, 200

