from datetime import datetime, timezone
from typing import Any, DefaultDict

from pynamodb.attributes import (MapAttribute, UnicodeAttribute,
                                 UTCDateTimeAttribute)
from pynamodb.models import Model
from pynamodb_attributes import IntegerAttribute

from app.models._meta import pynamodb_table_meta


class Conversation(Model):
    """Table representing a conversation."""
    Meta = pynamodb_table_meta("relay-conversations")  # type: ignore

    # Conversation attributes
    id = IntegerAttribute(hash_key=True)
    title = UnicodeAttribute(null=True)
    image = UnicodeAttribute(null=True)
    banner = UnicodeAttribute(null=True)
    bio = UnicodeAttribute(null=True)
    channels = MapAttribute(default=DefaultDict)  # type: ignore
    participants = MapAttribute(default=DefaultDict)  # type: ignore
    n_messages = IntegerAttribute(null=True)
    nuke_signature = UnicodeAttribute(null=True)
    created_ts = UTCDateTimeAttribute(null=True)
    last_updated_ts = UTCDateTimeAttribute(null=True)
    last_message_ts = UTCDateTimeAttribute(null=True)

    def save(self, *args: Any, **kwargs) -> Any:
        """Save conversation instance."""
        self.last_updated_ts = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)

    def as_dict(self) -> dict:
        """Conversation as hashmap."""
        hashmap = {}
        for key in self.attribute_values:
            hashmap[key] = self.__getattribute__(key)
        return hashmap
