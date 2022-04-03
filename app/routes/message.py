from flask import Blueprint, request

from app.models.user import User
from app.repositories import message as message_repo
from app.routes.decorators import authenticate_user

blueprint = Blueprint("message", __name__)


@blueprint.route("/message/send", methods=["POST"])
@authenticate_user
def send_message(user: User) -> dict:
    """Endpoint for sending a message."""
    request_data = request.get_json()

    convo_id = request_data.get("conversation_id")
    internal_key = request_data.get("internal_key")
    private_key = request_data.get("private_key")
    text = request_data.get("text")

    return message_repo.send_message(
        conversation_id=convo_id,
        internal_aes_key=internal_key,
        sender=user,
        text=text,
        private_key=private_key,
    )


@blueprint.route("/message/delete", methods=["POST"])
@authenticate_user
def delete_message(user: User) -> dict:
    """Endpoint for deleting a message."""
    request_data = request.get_json()

    message_id = request_data.get("message_id")

    return message_repo.delete_message(
        message_id=message_id,
        user=user,
    )
