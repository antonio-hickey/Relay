from flask import Blueprint, request

from app.repositories import user as user_repo
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
