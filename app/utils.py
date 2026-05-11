from datetime import datetime, timedelta
from uuid import UUID
import uuid_utils as uuid
from random import randint


def random_number():
    return randint(11000, 11999)


def generate_uuid7():
    return UUID(str(uuid.uuid7()))


def generate_delivery_date():
    return datetime.now() + timedelta(days=randint(1, 10))
