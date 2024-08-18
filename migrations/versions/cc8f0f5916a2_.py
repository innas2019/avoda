"""empty message

Revision ID: cc8f0f5916a2
Revises: adced6a87e2b
Create Date: 2024-08-08 13:46:23.325449

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc8f0f5916a2'
down_revision = 'adced6a87e2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('advt',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=40), nullable=False),
    sa.Column('phone', sa.String(length=40), nullable=True),
    sa.Column('contacts', sa.String(length=100), nullable=True),
    sa.Column('text', sa.String(length=500), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('priority', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('advt')
    # ### end Alembic commands ###
