"""add

Revision ID: 170b07a9cd5c
Revises: f3733342f5a2
Create Date: 2019-03-19 11:31:31.385881

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '170b07a9cd5c'
down_revision = 'f3733342f5a2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('news',
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=True),
    sa.Column('descrp', sa.String(length=255), nullable=True),
    sa.Column('image_url', sa.String(length=100), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('is_exam', sa.Integer(), nullable=True),
    sa.Column('reason', sa.String(length=100), nullable=True),
    sa.Column('cid', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['cid'], ['news_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('news')
    # ### end Alembic commands ###
