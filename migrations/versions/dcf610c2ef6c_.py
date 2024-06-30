"""empty message

Revision ID: dcf610c2ef6c
Revises: ead878374110
Create Date: 2024-06-06 13:37:17.874384

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dcf610c2ef6c'
down_revision = 'ead878374110'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('contacts', sa.String(length=40), nullable=True))
        
        batch_op.create_unique_constraint(None, ['contacts'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('phone',
               existing_type=sa.VARCHAR(length=40),
               nullable=False)
        batch_op.drop_column('contacts')

    # ### end Alembic commands ###
