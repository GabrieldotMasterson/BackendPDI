from factory import api, db
from sqlalchemy import select
from flask import Blueprint, request
from spectree import Response
from pydantic import BaseModel
from flask_jwt_extended import current_user, jwt_required

from models.PDIModel import Talks, TalksResponse, TalksResponseList, TalksCreate, SearchModel
from utils.responses import DefaultResponse
from datetime import datetime

talk_controller = Blueprint("talk_controller", __name__, url_prefix="/talks")

TALKS_PER_PAGE = 5


#; pode usa sem login
# ex de endpoint: /talks?search=python&page=2
@talk_controller.get("/")
@api.validate(
    query=SearchModel,   resp=Response(HTTP_200=TalksResponseList),tags=["talks"]
)
def get_all():
    search = request.args.get("search", "")
    page = int(request.args.get("page", 1))

    talks_query = select(Talks).filter(Talks.title.ilike(f"%{search}%"))

    talks_pagination = db.paginate(
        talks_query,
        page=page,
        per_page=TALKS_PER_PAGE,
        error_out=False,
    )
    pages =talks_pagination.pages
    total = talks_pagination.total
    talks = talks_pagination.items

    response = TalksResponseList(
        id=0,
        page=page,
        pages=pages,
        total=total,
        talks=[TalksResponse.model_validate(talk) for talk in talks], ).model_dump()

    return response, 200


@talk_controller.get("/<int:talk_id>")
@api.validate(
    resp=Response(HTTP_200=TalksResponse, HTTP_404=DefaultResponse),
    tags=["talks"]
)
def get_one(talk_id):

    talk = db.session.get(Talks, talk_id)

    if not talk:
        return {"msg": "Palestra não existe"}, 404

    response = TalksResponse.model_validate(talk).model_dump()
    return response, 200

@talk_controller.post("/")
@api.validate(json=TalksCreate, resp=Response(HTTP_201=DefaultResponse), tags=["talks"])
@jwt_required()
def create_talk():
    data = request.json

    startsAt = None
    if data.get("starts_at"):
        startsAt = datetime.fromisoformat(data["starts_at"])  # ← conversão correta

    talk = Talks(
        title=data["title"],
        description=data.get("description"),
        speaker_id=current_user.id,
        speaker_name=data.get("speaker_name"),
        starts_at=startsAt
    )

    db.session.add(talk)
    db.session.commit()

    return {"msg": f"Palestra {talk.title} criada."}, 201


@talk_controller.put("/<int:talk_id>")
@api.validate(
    json=TalksCreate,
    resp=Response(
        HTTP_200=DefaultResponse, HTTP_403=DefaultResponse, HTTP_404=DefaultResponse
    ),
    tags=["talks"],
)

@jwt_required()
def update_talk(talk_id):
    talk = db.session.get(Talks, talk_id)

    if talk is None:
        return {"msg": "Palestra não existe"}, 404

    if not (talk.speaker_id == current_user.id or current_user.role.can_manage_talks):
        return {"msg": "Voce não tem permissão para modificar essa palestra"}, 403

    data = request.json
    talk.title = data["title"]
    talk.description = data.get("description")
    talk.starts_at = data.get("starts_at")

    db.session.commit()
    return {"msg": "The talk was updated."}, 200


@talk_controller.delete("/<int:talk_id>")
@api.validate(
    resp=Response(
        HTTP_200=DefaultResponse, HTTP_403=DefaultResponse, HTTP_404=DefaultResponse
    ),
    tags=["talks"],
)
@jwt_required()
def delete_talk(talk_id):
    talk = db.session.get(Talks, talk_id)

    if talk is None:
        return {"msg": "Palestra não existe"}, 404

    if not (talk.speaker_id == current_user.id or current_user.role.can_manage_talks):
        return {"msg": "Voce não tem permissão para modificar essa palestra"}, 403

    db.session.delete(talk)
    db.session.commit()

    return {"msg": "Palestra excluida"}, 200
