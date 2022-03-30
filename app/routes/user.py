from flask import Blueprint, request

from app.models.user import User
from app.repositories import user as user_repo
from app.routes.decorators import authenticate_user
from app.util.error_library import get_error
from app.util.exceptions import UsernameExistsException

blueprint = Blueprint("user", __name__)


@blueprint.route("/user/sign-up", methods=["POST"])
def sign_up():
    request_data = request.get_json()

    username = request_data.get("username")
    password = request_data.get("password")

    try:
        if user_repo.get_user_by_username(username=username):
            return get_error("user_already_exists")
    except UsernameExistsException as e:
        return e.error_description, e.status_code
    except Exception:
        return get_error("internal_server_error")

    return user_repo.register_user(username=username, password=password)


@blueprint.route("/user/sign-in", methods=["POST"])
def sign_in():
    request_data = request.get_json()

    username = request_data.get("username")
    password = request_data.get("password")

    return {"result": user_repo.sign_in(username, password)}


@blueprint.route("/user/sign-out", methods=["POST"])
def sign_out():
    request_data = request.get_json()

    token = request_data.get("session_token")

    return {"result": user_repo.sign_out(token)}


@blueprint.route("/user/contacts/initiate", methods=["POST"])
@authenticate_user
def initiate_contact(user: User):
    request_data = request.get_json()

    initiator_id = user.id
    target_id = request_data.get("target_id")
    user_repo.initiate_contact(initiator=initiator_id, target=target_id)

    return {"Success": 200}


@blueprint.route("/user/contacts/accept", methods=["POST"])
@authenticate_user
def accept_key_exchange(user: User):
    request_data = request.get_json()

    initiator_id = user.id
    target_id = request_data.get("target_id")
    private_key = request_data.get("internal_key")

    user_repo.accept_contact(
        initiator=initiator_id,
        internal_key=private_key,
        target=target_id,
    )

    return {"Success": 200}


@blueprint.route("/user/contacts/confirm", methods=["POST"])
@authenticate_user
def confirm_key_exchange(user: User):
    request_data = request.get_json()

    initiator_id = user.id
    target_id = request_data.get("target_id")
    private_key = request_data.get("internal_key")

    user_repo.confirm_contact(
        initiator=initiator_id,
        internal_key=private_key,
        target=target_id,
    )

    return {"Success": 200}
