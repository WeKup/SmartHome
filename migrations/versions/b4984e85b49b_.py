"""empty message

Revision ID: b4984e85b49b
Revises: 3d15e00bb93a
Create Date: 2025-04-05 21:31:58.059381

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4984e85b49b'
down_revision = '3d15e00bb93a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nbMO', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('nbMO')

    # ### end Alembic commands ###
