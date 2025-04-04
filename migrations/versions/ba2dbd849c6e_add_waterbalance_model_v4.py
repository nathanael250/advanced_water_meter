"""Add WaterBalance model v4

Revision ID: ba2dbd849c6e
Revises: 5d59347f120a
Create Date: 2025-04-02 08:04:33.394139

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba2dbd849c6e'
down_revision = '5d59347f120a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('water_balance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('cubic_meters', sa.Float(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('water_balance')
    # ### end Alembic commands ###
