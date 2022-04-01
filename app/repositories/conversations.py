import uuid
from datetime import datetime, timezone

from app.models.conversation import Conversation
from app.repositories import crypto
from app.repositories.crypto import sign, verify_sign
from app.repositories.user import must_get_user_by_id
from app.util.error_library import get_error

# Conversation Access Level's
ADMIN: dict = {
    "role": "Creator",
    "access_level": "admin",
    "status": "",
}
MOD: dict = {
    "role": "moderator",
    "access_level": "mod",
    "status": "",
}
NORM: dict = {
    "role": "participant",
    "access_level": "norm",
    "status": "",
}


def get_conversation_by_id(conversation_id: int) -> Conversation:
    """Get a conversation by it's id."""
    return Conversation.get(hash_key=conversation_id)


def create_conversation(creator_id: int, title: str, private_key: str,
                        norm_ids: list[int], mod_ids: list[int],
                        image: str, banner: str, public_key_n: str) -> dict:
    """
    Create a conversation.

    A conversation is a collection of participants and
    messages. This is the room that host communication
    to the people inside it. There are 3 access levels
    in a conversation where:
        ADMIN => Creator of the conversation
        MOD => Privileged user in conversation
        NORM => Normal user in conversation
    """
    timestamp = datetime.now(timezone.utc)

    ADMIN["joined_ts"] = str(timestamp)
    ADMIN["last_update_ts"] = str(timestamp)
    admin: dict = {str(creator_id): ADMIN}

    MOD["joined_ts"] = str(timestamp)
    MOD["last_update_ts"] = str(timestamp)
    mods: dict = {str(mod_id): MOD for mod_id in mod_ids}

    NORM["joined_ts"] = str(timestamp)
    NORM["last_update_ts"] = str(timestamp)
    norms: dict = {str(norm_id): NORM for norm_id in norm_ids}

    participants = admin | mods | norms

    # Create conversation
    conversation = Conversation()
    id = int(str(uuid.uuid1().int)[:30])

    # Create nuke signature
    signature = crypto.sign(
        message=f"nuke {str(id)[:10]}",
        priv_key=private_key,
        pub_key_n=public_key_n,
    )

    # Set conversation attributes
    conversation.id = id
    conversation.title = title
    conversation.image = image
    conversation.banner = banner
    conversation.bio = ""
    conversation.participants = participants
    conversation.n_messages = 0
    conversation.nuke_signature = signature
    conversation.created_ts = timestamp
    conversation.last_message_ts = timestamp

    conversation.save()

    return {
        "msg": "Successfully created conversation",
        "status_code": 200,
    }


def nuke_conversation(user_id: int,
                      conversation_id: int,
                      private_key: str) -> dict:
    """Delete a conversation. (Not reversable)"""
    user = must_get_user_by_id(user_id)
    rsa_pub_n = user.rsa_pub_key_n
    rsa_pub_e = user.rsa_pub_key_e
    signature = sign(
        message=f"delete conversation: {conversation_id}",
        priv_key=private_key,
        pub_key_n=rsa_pub_n,
    )

    verified = verify_sign(
        message=f"delete conversation: {conversation_id}",
        signature=signature,
        pub_key_n=rsa_pub_n,
        pub_key_e=rsa_pub_e,
    )

    if verified is False:
        return get_error("invalid_signature")

    convo = get_conversation_by_id(conversation_id)
    convo.delete()

    return {
        "msg": f"Successfully nuked conversation: {conversation_id}",
        "status_code": 200,
    }


def update_conversation(conversation_id: int,
                        user_id: int,
                        title: str,
                        image: str,
                        banner: str,
                        bio: str) -> dict:
    """Update the conversation."""
    timestamp = datetime.now(timezone.utc)

    convo = get_conversation_by_id(conversation_id)
    if convo.participants[str(user_id)]["access_level"] == "norm":
        return get_error("access_level_not_high_enough")

    convo.title = title
    convo.image = image
    convo.banner = banner
    convo.bio = bio
    convo.last_updated_ts = timestamp

    convo.save()

    return {
        "msg": f"Successfully updated conversation {conversation_id}",
        "status_code": 200,
    }


def add_participant(conversation_id: int,
                    user_id: int,
                    role: str,
                    access_level: str,
                    target_participant_id: int) -> dict:
    """Add participant to conversation."""
    timestamp = datetime.now(timezone.utc)
    convo = get_conversation_by_id(conversation_id)

    if convo.participants[str(user_id)]["access_level"] == "norm":
        return get_error("access_level_not_high_enough")

    if access_level == "norm":
        NORM["joined_ts"] = str(timestamp)
        NORM["last_update_ts"] = str(timestamp)
        NORM["role"] = role
        convo.participants[str(target_participant_id)] = NORM

    elif access_level == "mod":
        MOD["joined_ts"] = str(timestamp)
        MOD["last_update_ts"] = str(timestamp)
        MOD["role"] = role
        convo.participants[str(target_participant_id)] = MOD

    else:
        return get_error("invalid_access_level")

    convo.save()

    return {
        "msg": "Successfully added participant",
        "status_code": 200,
    }


def remove_participant(conversation_id: int,
                       user_id: int,
                       target_id: int) -> dict:
    """Add participant to conversation."""
    convo = get_conversation_by_id(conversation_id)

    participants = convo.participants

    if participants[str(user_id)]["access_level"] == "norm":
        return get_error("access_level_not_high_enough")

    participants[str(target_id)] = None
    convo.save()

    return {
        "msg": "Successfully removed participant",
        "status_code": 200,
    }


def update_participant(conversation_id: int,
                       participant_id: int,
                       role: str,
                       access_level: str,
                       status: str) -> dict:
    """Update a participant of a conversation."""
    timestamp = datetime.now(timezone.utc)
    convo = get_conversation_by_id(conversation_id)

    participant = convo.participants[str(participant_id)]
    participant["role"] = role
    participant["access_level"] = access_level
    participant["status"] = status
    participant["last_update_ts"] = str(timestamp)

    convo.participants[str(participant_id)] = participant
    convo.save()

    return {
        "msg": f"Successfully updated participant: {participant_id}",
        "status_code": 200,
    }
