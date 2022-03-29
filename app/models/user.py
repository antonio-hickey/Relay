from datetime import datetime, timezone
from typing import Any, DefaultDict

from pynamodb.attributes import (MapAttribute, UnicodeAttribute,
                                 UTCDateTimeAttribute)
from pynamodb.indexes import GlobalSecondaryIndex
from pynamodb.models import Model
from pynamodb_attributes import IntegerAttribute

from app.models._meta import pynamodb_index_meta, pynamodb_table_meta


class NameIndex(GlobalSecondaryIndex):
    """Search on usernames."""
    Meta = pynamodb_index_meta(hash_key="name", range_key=None)
    username_search = UnicodeAttribute(hash_key=True)


class User(Model):
    """Table representing the user."""
    Meta = pynamodb_table_meta("relay-users")

    # User attributes
    id = IntegerAttribute(hash_key=True)
    name = UnicodeAttribute(null=True)
    password_hashed = UnicodeAttribute(null=True)
    rsa_pub_key_n = UnicodeAttribute(null=True)
    rsa_pub_key_e = UnicodeAttribute(null=True)
    aes_internal = UnicodeAttribute(null=True)
    contacts = MapAttribute(default=DefaultDict)
    created_ts = UTCDateTimeAttribute(null=True)
    last_update_ts = UTCDateTimeAttribute(null=True)

    # User search indexes
    username_search = NameIndex()

    def save(self, *args: Any, **kwargs) -> Any:
        """Save user instance"""
        self.last_updated_ts = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)

    def as_dict(self) -> dict:
        """User as hashmap."""
        hashmap = {}
        for key in self.attribute_values:
            hashmap[key] = self.__getattribute__(key)
        return hashmap
