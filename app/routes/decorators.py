from functools import wraps

from flask import request

from app import session
from app.models.user import User
from app.util.error_library import get_error


def authenticate_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        request_data = request.get_json()

        session_token = request_data.get("session_token")

        if not session_token:
            return get_error("no_session_token_provided")

        if session_token not in session.active_users:
            return get_error("incorrect_session_token")

        user: User = session.active_users[session_token]

        return f(user, *args, **kwargs)

    return decorated
