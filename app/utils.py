from datetime import datetime, timedelta, timezone
from uuid import UUID
import uuid_utils as uuid
from random import randint


def generate_uuid7() -> UUID:
    return UUID(str(uuid.uuid7()))


def generate_delivery_date():
    return datetime.now(timezone.utc) + timedelta(days=randint(1, 10))
