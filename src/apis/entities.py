from datetime import date as d

from app_context import db
from common.constants import DateStatusEnum
from common.logger import logging
from models import Currency, Date, DateCurrencyRate


class BaseEntity:
    _loaded_object = None

    def read(self):
        filters = []
        for key, value in self.__dict__.items():
            if value != None:
                key = key[1:] if key.startswith('_') else key
                filters.append(getattr(self._model, key) == value)
        return self.query.filter(db.and_(*filters)).one()

    def insert(self):
        self._load_object()
        db.session.add(self.loaded_object)
        db.session.commit()
        return self.loaded_object

    def update(self, key: str, value):
        setattr(self._loaded_object, key, value)
        db.session.commit()
        return self.loaded_object

    def _load_object(self):
        self._loaded_object = self._load_to_model()

    def _get_entity(self, entity, field):
        if entity.loaded_object is None:
            element = entity.query.filter(getattr(entity._model, field) == getattr(entity, f'_{field}')).one_or_none()
            if element:
                entity.loaded_object = element
                logging.debug(entity.loaded_object)
            else:
                entity.insert()
        return entity

    @property
    def query(self):
        return self._model.query

    @property
    def loaded_object(self):
        return self._loaded_object

    @loaded_object.setter
    def loaded_object(self, value):
        self._loaded_object = value


class CurrencyEntity(BaseEntity):
    _model = Currency

    def __init__(self,
                 uuid: str = None,
                 code: str = None):
        self._uuid = uuid
        self._code = code

    def _load_to_model(self):
        return self._model(code=self._code)


class DateEntity(BaseEntity):
    _model = Date

    def __init__(self,
                 uuid: str = None,
                 date: d = None,
                 status: DateStatusEnum = None):
        self._uuid = uuid
        self._date = date
        self._status = status

    @classmethod
    def query_last(cls):
        return cls._model.query.order_by(db.desc(cls._model.date)).limit(1).one_or_none()

    def _load_to_model(self):
        return self._model(date=self._date)


class DateCurrencyRateEntity(BaseEntity):
    _model = DateCurrencyRate

    def __init__(self,
                 date: DateEntity,
                 currency: CurrencyEntity,
                 amount: float,
                 epoch: float,
                 base_ccy: str):
        self._date = self._get_entity(date, 'date')
        self._currency = self._get_entity(currency, 'code')
        self._amount = amount
        self._epoch = epoch
        self._base_ccy = base_ccy

    def _load_to_model(self):
        return self._model(
            date_uuid=self._date.loaded_object.uuid,
            currency_uuid=self._currency.loaded_object.uuid,
            amount=self._amount,
            epoch=self._epoch,
            base_ccy=self._base_ccy
        )
