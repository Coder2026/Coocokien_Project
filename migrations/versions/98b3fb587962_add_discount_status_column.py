"""Add discount_status column

Revision ID: 98b3fb587962
Revises: a24a88ec6ed6
Create Date: 2024-11-15 20:54:42.700173

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98b3fb587962'
down_revision = 'a24a88ec6ed6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('voucher', schema=None) as batch_op:
        batch_op.add_column(sa.Column('discount_status', sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('voucher', schema=None) as batch_op:
        batch_op.drop_column('discount_status')

    # ### end Alembic commands ###