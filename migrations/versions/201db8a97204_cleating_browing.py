"""cleating browing

Revision ID: 201db8a97204
Revises: 5fba881c38dc
Create Date: 2025-03-20 19:07:00.993202

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '201db8a97204'
down_revision = '5fba881c38dc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('credit_limit', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('credit_limit')

    # ### end Alembic commands ###
