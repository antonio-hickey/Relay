import random
import string
import uuid
from datetime import datetime, timezone
from hashlib import sha256
from random import randint as random_integer
from typing import Optional

from Crypto.PublicKey import RSA
from pynamodb.exceptions import PutError

from app import session
from app.models.user import User
from app.repositories import crypto
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
    """
    User sign in.

    Find user by username passed, and compare the password hash.
    If successful return a session token for them to stay logged in,
    else return error corresponding to the issue.
    """
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
    """
    User sign out.

    Revoke the session token forcing the user to have
    to sign back in to regenerate a session token.
    """
    try:
        session.revoke_token(session_token)
    except Exception:
        return {"msg": "Failed to sign out!", "status_code": 500}
    return {
        "msg": "Successfully signed out!",
        "status_code": 200,
    }


def register_user(username: str, password: str) -> dict:
    """
    Register a user.

    Check if username already exists else hash the password
    and create a user, rendering their attributes.
    """
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


def initiate_contact(initiator: int, target: int) -> None:
    """
    Request contact with another user.

    Create a private key, set public prime and base,
    and create my contact map to give to target user.

    a := my private key
    p := our public prime
    g := our public base
    A := my public solution
    """
    me = must_get_user_by_id(initiator)

    a = random_integer(2, 100)  # Never stored not even user knows this key
    p = random_integer(2, 100)
    g = random_integer(2, 100)
    while g > p:  # Make sure the base is less than the prime
        g = random_integer(2, 100)

    A = (g ** a) % p
    my_contact = {
        "name": me.name,
        "shared_prime": p,
        "shared_base": g,
        "their_shared": A,
        "rsa_pub": me.rsa_pub_key_n,
    }

    you = must_get_user_by_id(target)
    you.contacts[str(me.id)] = my_contact
    you.save()


def accept_contact(initiator: int, internal_key: str, target: int) -> None:
    """
    Accept contact request from another user.

    Create private key and use it with the public prime,
    and base to render a solution. Then create a contact
    map for me to give to the target user, and computing
    then encrypting our shared private key.

    b := my private key
    p := public prime
    g := public base
    B := my public solution
    A := their public solution
    k := our shared private key
    """
    me = must_get_user_by_id(initiator)
    target_contact = me.contacts[str(target)]

    b = random_integer(2, 100)  # Never stored not even user knows this key

    p = target_contact["shared_prime"]
    g = target_contact["shared_base"]
    A = target_contact["their_shared"]

    B = (g ** b) % p
    k = (g ** (B * A) % p)
    my_contact = {
        "name": me.name,
        "shared_prime": p,
        "shared_base": g,
        "their_shared": B,
        "rsa_pub": me.rsa_pub_key_n,
    }

    you = must_get_user_by_id(target)
    you.contacts[str(me.id)] = my_contact
    try:
        you.save()
    except PutError:
        pass

    target_contact = me.contacts[str(target)]
    target_contact["shared_private_key"] = crypto.encrypt(str(k), key=internal_key)

    you.contacts[str(me.id)]["aes_key"] = crypto.encrypt(internal_key, str(k))

    you.save()
    me.save()


def confirm_contact(initiator: int, internal_key: str, target: int) -> None:
    """
    Finilize contact.

    Compute and encrypt our shared private key, finishing the key
    exchange as we both now have our shared private key. We have
    to use our internal key to decrypt our shared private key though.

    p := public prime
    g := public base
    B := my public solution
    A := their public solution
    k := our shared private key
    """
    me = must_get_user_by_id(initiator)
    target_user = must_get_user_by_id(target)

    target_contact = me.contacts[str(target)]
    g, p = target_contact["shared_base"], target_contact["shared_prime"]
    B = target_contact["their_shared"]
    A = target_user.contacts[str(initiator)]["their_shared"]
    k = g ** (A * B) % p
    target_contact["shared_private_key"] = crypto.encrypt(str(k), key=internal_key)
    target_user.contacts[str(initiator)]["aes_key"] = crypto.encrypt(internal_key, str(k))

    me.save()
    target_user.save()


def update_user(user: User) -> None:
    """Update a user."""
    user.save()
