from flask import Blueprint, request

from app.models.user import User
from app.repositories import conversations as convo_repo
from app.routes.decorators import authenticate_user

blueprint = Blueprint("conversation", __name__)


@blueprint.route("/conversation/create", methods=["POST"])
@authenticate_user
def create_conversation(user: User):
    request_data = request.get_json()

    creator_id = user.id
    title = request_data.get("title")
    norm_participant_ids = request_data.get("norm_user_ids")
    mod_participant_ids = request_data.get("mod_user_ids")
    image = request_data.get("image")
    banner = request_data.get("banner")
    private_key = request_data.get("private_key")
    public_key = user.rsa_pub_key_n

    return convo_repo.create_conversation(
        creator_id=creator_id,
        private_key=private_key,
        public_key_n=public_key,
        title=title,
        norm_ids=norm_participant_ids,
        mod_ids=mod_participant_ids,
        image=image,
        banner=banner,
    )


@blueprint.route("/conversation/nuke", methods=["POST"])
@authenticate_user
def nuke_conversation(user: User):
    request_data = request.get_json()

    conv_id = request_data.get("conversation_id")
    private_key = request_data.get("private_key")

    return convo_repo.nuke_conversation(
        user_id=user.id,
        conversation_id=conv_id,
        private_key=private_key,
    )


@blueprint.route("/conversation/update", methods=["POST"])
@authenticate_user
def update_conversation(user: User):
    request_data = request.get_json()

    convo_id = request_data.get("conversation_id")
    title = request_data.get("title")
    image = request_data.get("image")
    banner = request_data.get("banner")
    bio = request_data.get("bio")

    return convo_repo.update_conversation(
        conversation_id=convo_id,
        user_id=user.id,
        title=title,
        image=image,
        banner=banner,
        bio=bio,
    )


@blueprint.route("/conversation/participants/update", methods=["POST"])
@authenticate_user
def update_participant(user: User):
    request_data = request.get_json()

    convo_id = request_data.get("conversation_id")
    target_id = request_data.get("target_id")
    role = request_data.get("role")
    access_level = request_data.get("access_level")
    status = request_data.get("status")

    return convo_repo.update_participant(
        conversation_id=convo_id,
        participant_id=target_id,
        role=role,
        access_level=access_level,
        status=status,
    )


@blueprint.route("/conversation/participants/add", methods=["POST"])
@authenticate_user
def add_participant(user: User):
    request_data = request.get_json()

    convo_id = request_data.get("conversation_id")
    target_participant_id = request_data.get("target_participant_id")
    role = request_data.get("role")
    access_level = request_data.get("access_level")

    return convo_repo.add_participant(
        conversation_id=convo_id,
        user_id=user.id,
        role=role,
        access_level=access_level,
        target_participant_id=target_participant_id,
    )


@blueprint.route("/conversation/participants/remove", methods=["POST"])
@authenticate_user
def remove_participant(user: User):
    request_data = request.get_json()

    convo_id = request_data.get("conversation_id")
    target_id = request_data.get("target_id")

    return convo_repo.remove_participant(
        conversation_id=convo_id,
        user_id=user.id,
        target_id=target_id,
    )


@blueprint.route("/conversations/channel/create", methods=["POST"])
@authenticate_user
def create_channel(user: User):
    request_data = request.get_json()

    convo_id = request_data.get("conversation_id")
    channel_title = request_data.get("channel_title")
    channel_roles = request_data.get("channel_roles")
    channel_access_levels = request_data.get("channel_access_levels")
    channel_message_timeout = request_data.get("channel_message_timeout")
    channel_req_signatures = request_data.get("channel_requires_signatures")

    return convo_repo.create_channel(
        conversation_id=convo_id,
        title=channel_title,
        roles=channel_roles,
        access_levels=channel_access_levels,
        message_timeout=channel_message_timeout,
        requires_signatures=channel_req_signatures,
    )


@blueprint.route("/conversations/channel/update", methods=["POST"])
@authenticate_user
def update_channel(user: User):
    request_data = request.get_json()

    convo_id = request_data.get("conversation_id")
    channel_id = request_data.get("channel_id")
    channel_title = request_data.get("channel_title")
    channel_roles = request_data.get("channel_roles")
    channel_access_levels = request_data.get("channel_access_levels")
    channel_message_timeout = request_data.get("channel_message_timeout")
    channel_req_signatures = request_data.get("channel_requires_signatures")

    return convo_repo.update_channel(
        conversation_id=convo_id,
        channel_id=channel_id,
        title=channel_title,
        roles=channel_roles,
        access_levels=channel_access_levels,
        message_timeout=channel_message_timeout,
        requires_signatures=channel_req_signatures,
    )


@blueprint.route("/conversations/channel/remove", methods=["POST"])
@authenticate_user
def delete_channel(user: User):
    request_data = request.get_json()

    convo_id = request_data.get("conversation_id")
    channel_id = request_data.get("channel_id")

    return convo_repo.delete_channel(
        conversation_id=convo_id,
        channel_id=channel_id,
    )
