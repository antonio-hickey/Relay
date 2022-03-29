from app.util.http_error_codes import (HTTP_CONFLICT,
                                       HTTP_INTERNAL_SERVER_ERROR,
                                       HTTP_UNAUTHORIZED)

error_dict = {
    "user_already_exists": {
        "msg": "An account underneath this username has already been made",
        "error_code": HTTP_CONFLICT,
    },
    "user_does_not_exist": {
        "msg": "An account with this username does not exist!",
        "error_code": HTTP_UNAUTHORIZED,
    },
    "user_password_incorrect": {
        "msg": "Incorrect password!",
        "error_code": HTTP_UNAUTHORIZED,
    },
    "internal_server_error": {
        "msg": "Internal Server Error",
        "error_code": HTTP_INTERNAL_SERVER_ERROR,
    },
}


def get_error(error: str) -> dict:
    error_record = error_dict.get(error)

    return error_record if error_record else {"msg": "Error not indexed", "error_code": 500}
