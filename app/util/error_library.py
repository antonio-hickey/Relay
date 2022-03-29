from typing import Any, Tuple, Union

from app.util.http_error_codes import HTTP_CONFLICT, HTTP_INTERNAL_SERVER_ERROR

error_dict = {
    "user_already_exists": {
        "msg": "An account underneath this username has already been made",
        "error_code": HTTP_CONFLICT,
    },
    "internal_server_error": {
        "msg": "Internal Server Error",
        "error_code": HTTP_INTERNAL_SERVER_ERROR,
    },
}


def get_error(error: str) -> Tuple[Union[object, Any], Union[object, Any]]:
    error_record = error_dict.get(error)

    if error_record:
        return (error_record["msg"], error_record["error_code"])
    return ("Error not indexed", 500)
