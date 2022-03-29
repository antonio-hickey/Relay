from app.models.session_token import Token
from app.models.user import User

# Hashmap with session token as key and a user as the value
active_users: dict[str, User] = {}


def add_user(user: User) -> str:
    """Add a user to a sessions active users"""
    token = Token(user.id).value
    active_users[token] = user
    return token


def revoke_token(token: str) -> None:
    """Remove a user from a sessions active users"""
    del active_users[token]
