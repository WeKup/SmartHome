"""empty message

Revision ID: 53739e67c883
Revises: 99e89f7c2353
Create Date: 2025-04-05 21:17:29.409626

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53739e67c883'
down_revision = '99e89f7c2353'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nbR', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('nbA', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('nbAROOM', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('nbAType', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('nbD', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('nbM', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('nbM')
        batch_op.drop_column('nbD')
        batch_op.drop_column('nbAType')
        batch_op.drop_column('nbAROOM')
        batch_op.drop_column('nbA')
        batch_op.drop_column('nbR')

    # ### end Alembic commands ###
