"""empty message

Revision ID: ead878374110
Revises: 2a90a1600094
Create Date: 2024-05-16 22:15:18.976329

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ead878374110'
down_revision = '2a90a1600094'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('issend', sa.Integer(), nullable=True))
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=40),
               type_=sa.String(length=256),
               existing_nullable=False)
        batch_op.alter_column('settings',
               existing_type=sa.VARCHAR(length=40),
               type_=sa.String(length=256),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('settings',
               existing_type=sa.String(length=256),
               type_=sa.VARCHAR(length=40),
               existing_nullable=True)
        batch_op.alter_column('password',
               existing_type=sa.String(length=256),
               type_=sa.VARCHAR(length=40),
               existing_nullable=False)
        batch_op.drop_column('issend')

    # ### end Alembic commands ###
