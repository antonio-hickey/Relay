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
    conversation.channels = {}
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
    """Remove participant from a conversation."""
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


def create_channel(conversation_id: int,
                   title: str,
                   roles: list[str] = [],
                   access_levels: list[str] = [],
                   message_timeout: int = 5,
                   requires_signatures: bool = False) -> dict:
    """Create a new channel in a conversation."""
    timestamp = datetime.now(timezone.utc)
    convo = get_conversation_by_id(conversation_id)
    id = int(str(uuid.uuid1().int)[:30])

    convo.channels[str(id)] = {
        "title": title,
        "access_levels": access_levels,
        "roles": roles,
        "message_timeout": message_timeout,
        "requires_signatures": requires_signatures,
        "created_ts": str(timestamp),
        "last_update_ts": str(timestamp),
    }
    convo.save()

    return {
        "msg": "Successfully created channel.",
        "status_code": 200,
    }


def update_channel(conversation_id: int,
                   channel_id: int,
                   title: str = "",
                   roles: list[str] = [],
                   access_levels: list[str] = [],
                   message_timeout: int = 5,
                   requires_signatures: bool = False) -> dict:
    """Update a channel inside a conversation."""
    timestamp = datetime.now(timezone.utc)
    convo = get_conversation_by_id(conversation_id)
    channel = convo.channels[str(channel_id)]

    if title != "":
        channel["title"] = title
    if roles != []:
        channel["roles"] = roles
    if access_levels != []:
        channel["access_levels"] = access_levels
    if message_timeout != 5:
        channel["message_timeout"] = message_timeout
    if requires_signatures != channel["requires_signatures"]:
        channel["requires_signatures"]

    channel["last_update_ts"] = str(timestamp)
    convo.save()

    return {
        "msg": "Successfully updated channel.",
        "status_code": 200,
    }


def delete_channel(conversation_id: int,
                   channel_id: int) -> dict:
    """Delete a channel inside a conversation."""
    convo = get_conversation_by_id(conversation_id)
    channels = convo.channels.as_dict()
    del channels[str(channel_id)]

    convo.channels = channels
    convo.save()

    return {
        "msg": "Successfully deleted channel.",
        "status_code": 200,
    }
