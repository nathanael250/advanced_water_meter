"""Add transaction_type to Payment model

Revision ID: 9f4c16acfee2
Revises: 41a5bc101c35
Create Date: 2025-03-27 17:29:26.861782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f4c16acfee2'
down_revision = '41a5bc101c35'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('transaction_type', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.drop_column('transaction_type')

    # ### end Alembic commands ###
