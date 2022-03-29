from datetime import datetime, timezone
from random import randint as random_integer


class Token:
    """A token for user's to stay logged in."""
    def __init__(self, user_id: int) -> None:
        self.user_id: int = user_id
        self.created_ts = datetime.now(timezone.utc)
        self.value: str = hex(
            user_id + random_integer(1, 999999999999),
        )

    def new(self) -> None:
        """Generate a new token for a user."""
        self.value = hex(
            self.user_id + random_integer(1, 999999999999),
        )
