from uuid import uuid4

from sqlalchemy_utils import UUIDType

from app_context import db
from common.constants import DateStatusEnum


class Date(db.Model):
    __tablename__ = 'date'

    uuid = db.Column(UUIDType(binary=False), default=uuid4, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    status = db.Column(db.Integer, default=DateStatusEnum.PENDING.value, nullable=False)
