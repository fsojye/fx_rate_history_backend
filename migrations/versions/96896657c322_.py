"""empty message

Revision ID: 96896657c322
Revises: 
Create Date: 2022-03-03 23:19:29.136748

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '96896657c322'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('currency',
    sa.Column('uuid', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
    sa.Column('code', sa.String(length=32), nullable=False),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('code')
    )
    op.create_table('date',
    sa.Column('uuid', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('date')
    )
    op.create_table('date_currency_rate',
    sa.Column('uuid', sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
    sa.Column('date_uuid', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.Column('currency_uuid', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('epoch', sa.String(length=32), nullable=False),
    sa.Column('base_ccy', sa.String(length=32), nullable=False),
    sa.ForeignKeyConstraint(['currency_uuid'], ['currency.uuid'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['date_uuid'], ['date.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('date_currency_rate')
    op.drop_table('date')
    op.drop_table('currency')
    # ### end Alembic commands ###
