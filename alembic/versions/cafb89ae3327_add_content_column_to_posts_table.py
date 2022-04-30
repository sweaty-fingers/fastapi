"""add content column to posts table

Revision ID: cafb89ae3327
Revises: d570e336525d
Create Date: 2022-05-01 00:10:03.200371

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cafb89ae3327'
down_revision = 'd570e336525d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_column('posts', 'content')
    pass
