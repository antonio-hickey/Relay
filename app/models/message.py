from datetime import datetime, timezone
from typing import Any

from pynamodb.attributes import (BooleanAttribute, UnicodeAttribute,
                                 UTCDateTimeAttribute)
from pynamodb.models import Model
from pynamodb_attributes import IntegerAttribute

from app.models._meta import pynamodb_table_meta


class Message(Model):
    """Table representing messages."""
    Meta = pynamodb_table_meta("relay-message")  # type: ignore

    # Message attributes
    id = IntegerAttribute(hash_key=True)
    conversation = IntegerAttribute(null=True)
    sender = IntegerAttribute(null=True)
    message_text = UnicodeAttribute(null=True)
    signature = UnicodeAttribute(null=True)
    verified = BooleanAttribute(null=True)
    sent_ts = UTCDateTimeAttribute(null=True)

    def save(self, *args: Any, **kwargs) -> Any:
        """Save message instance"""
        self.last_updated_ts = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)

    def as_dict(self) -> dict:
        """Message as hashmap."""
        hashmap = {}
        for key in self.attribute_values:
            hashmap[key] = self.__getattribute__(key)
        return hashmap
