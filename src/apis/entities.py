from app_context import db
from common.constants import DateStatusEnum
from models import Date


class BaseEntity:
    def insert(self):
        pass

    @classmethod
    def query_last(cls):
        pass


class CurrencyEntity(BaseEntity):
    def __init__(self,
                 uuid: str = None,
                 code: str = None):
        self._uuid = uuid
        self._code = code


class DateEntity(BaseEntity):
    _model = Date

    def __init__(self,
                 uuid: str = None,
                 date: str = None,
                 status: DateStatusEnum = None):
        self._uuid = uuid
        self._date = date
        self._status = status

    @classmethod
    def query_last(cls):
        return cls._model.query.order_by(db.desc(cls._model.date)).limit(1).one()


class RateEntity(BaseEntity):
    def __init__(self,
                 date: DateEntity,
                 currency: CurrencyEntity,
                 amount: float,
                 epoch: float,
                 base_ccy: str):
        self._date = date
        self._currency = currency
        self._amount = amount
        self._epoch = epoch
        self._base_ccy = base_ccy
