"""Remove server prefix

Revision ID: d04cd6dff252
Revises: 851d11b8a33e
Create Date: 2021-08-03 21:10:58.749717

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "d04cd6dff252"
down_revision = "851d11b8a33e"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("guild", "prefix")


def downgrade():
    op.add_column("guild", sa.Column("guild", sa.Unicode(200)))
