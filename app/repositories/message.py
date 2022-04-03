import uuid
from datetime import datetime, timezone

from app.models.message import Message
from app.models.user import User
from app.repositories import crypto
from app.util.error_library import get_error


def get_message(message_id: int) -> Message:
    """Get a message by it's id."""
    return Message.get(hash_key=message_id)


def send_message(conversation_id: int,
                 internal_aes_key: str,
                 sender: User,
                 text: str,
                 private_key: str = None) -> dict:
    """Send a message to a conversation."""
    timestamp = datetime.now(timezone.utc)

    encrypted_text = crypto.encrypt(text, internal_aes_key)
    message_id = int(str(uuid.uuid4().int)[:30])

    if private_key:
        signature = crypto.sign(encrypted_text, private_key, sender.rsa_pub_key_n)
        verified = crypto.verify_sign(encrypted_text, signature, sender.rsa_pub_key_n, sender.rsa_pub_key_e)
    else:
        signature = ""
        verified = False

    message = Message()

    message.id = message_id
    message.conversation = conversation_id
    message.sender = sender.id
    message.message_text = encrypted_text
    message.signature = signature
    message.verified = verified
    message.sent_ts = timestamp

    message.save()

    return {
        "msg": "Message sent successfully",
        "status_code": 200,
    }


def delete_message(message_id: int, user: User) -> dict:
    """Delete your message."""
    message = get_message(message_id)

    if user.id == message.sender:
        message.delete()
        return {
            "msg": "Successfully deleted message",
            "status_code": 200,
        }

    else:
        return get_error("access_level_not_high_enough")
