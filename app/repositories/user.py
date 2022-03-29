import random
import string
import uuid
from datetime import datetime, timezone
from hashlib import sha256
from typing import Optional

from Crypto.PublicKey import RSA

from app import session
from app.models.user import User
from app.util.error_library import get_error
from app.util.exceptions import UsernameExistsException


def get_user_by_id(user_id: int) -> Optional[User]:
    """Get a user by their uuid."""
    user: Optional[User] = None
    try:
        user = User.get(hash_key=user_id)
    except User.DoesNotExist:
        user = None

    return user


def must_get_user_by_id(user_id: int) -> User:
    """Must get user by id (None is not an opt)"""
    return User.get(hash_key=user_id)


def get_user_by_username(username: str) -> Optional[User]:
    """Get a user by their username."""
    try:
        users = User.username_search.query(hash_key=username.lower())
    except Exception:
        return None
    users = list(users)  # type: ignore

    return users[0] if users else None  # type: ignore


def sign_in(username: str, password: str) -> dict:
    try:
        user: User = get_user_by_username(username)  # type: ignore
    except User.DoesNotExist:
        return get_error("user_does_not_exist")  # type: ignore

    password_hashed = hex(int.from_bytes(
        sha256(password.encode()).digest(),
        byteorder="big",
    ))

    if password_hashed == user.password_hashed:
        token = session.add_user(user)
        return {
            "msg": "Login Successful!",
            "session_token": token,
            "status_code": 200,
        }

    return get_error("user_password_incorrect")  # type: ignore


def sign_out(session_token: str) -> dict:
    try:
        session.revoke_token(session_token)
    except Exception:
        return {"msg": "Failed to sign out!", "status_code": 500}
    return {
        "msg": "Successfully signed out!",
        "status_code": 200,
    }


def register_user(username: str, password: str) -> dict:
    """Register a user."""
    timestamp = datetime.now(timezone.utc)

    # Check if username already exists
    if get_user_by_username(username):
        raise UsernameExistsException(error_description="This username already exists!")

    # Hash their password
    password_hashed: str = hex(int.from_bytes(
        sha256(password.encode()).digest(),
        byteorder='big',
    ))

    # Create user's rsa keys
    rsa_key_pair = RSA.generate(bits=2048)

    # Create aes internal key
    key = ''.join(random.choice(
        string.ascii_lowercase + string.ascii_uppercase + string.digits,
    ) for _ in range(15))

    # Create user
    user = User()

    # Set user attributes
    user.id = int(str(uuid.uuid1().int)[:30])
    user.name = username
    user.password_hashed = password_hashed
    user.rsa_pub_key_n = hex(rsa_key_pair.n)
    user.rsa_pub_key_e = hex(rsa_key_pair.e)
    user.contacts = {}
    user.created_ts = timestamp
    user.last_update_ts = timestamp

    user.save()

    return {"private_key": hex(rsa_key_pair.d), "internal_key": key}


def update_user(user: User):
    user.save()
