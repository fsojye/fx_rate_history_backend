from uuid import uuid4

from sqlalchemy_utils import UUIDType

from app_context import db
from common.constants import DateStatusEnum


class Date(db.Model):
    __tablename__ = 'date'

    uuid = db.Column(UUIDType(binary=False), default=uuid4, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    status = db.Column(db.Integer, default=DateStatusEnum.PENDING.value, nullable=False)
    rates = db.relationship("DateCurrencyRate", backref="date", lazy="dynamic")


class Currency(db.Model):
    __tablename__ = "currency"

    uuid = db.Column(UUIDType(binary=False), default=uuid4, primary_key=True)
    code = db.Column(db.String(32), unique=True, nullable=False)
    rates = db.relationship("DateCurrencyRate", backref="currency", lazy="dynamic")


class DateCurrencyRate(db.Model):
    __tablename__ = "date_currency_rate"

    uuid = db.Column(UUIDType(binary=False), default=uuid4, primary_key=True)
    date_uuid = db.Column(UUIDType, db.ForeignKey('date.uuid', ondelete="CASCADE"), nullable=False)
    currency_uuid = db.Column(UUIDType, db.ForeignKey('currency.uuid', ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    epoch = db.Column(db.String(32), nullable=False)
    base_ccy = db.Column(db.String(32), nullable=False)
