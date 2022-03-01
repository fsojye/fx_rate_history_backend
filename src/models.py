from pynamodb.attributes import UnicodeAttribute, NumberAttribute, ListAttribute

from app_context import db


class ProductLookup(db.Model):
    class Meta:
        table_name = "product_lookup"
        region = "us-west-2"

    name = UnicodeAttribute(hash_key=True)
    quantity = NumberAttribute(default_for_new=0)


class Order(db.Model):
    class Meta:
        table_name = "order"
        region = "us-west-2"

    order_uuid = UnicodeAttribute(hash_key=True)
    items = ListAttribute()
    status = UnicodeAttribute(default_for_new='PENDING')