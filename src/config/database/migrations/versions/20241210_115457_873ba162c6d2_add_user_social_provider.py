"""Add User.social_provider

Revision ID: 873ba162c6d2
Revises: b4e8dea4eed8
Create Date: 2024-12-10 11:54:57.150990

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '873ba162c6d2'
down_revision: Union[str, None] = 'b4e8dea4eed8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service_user', sa.Column('social_provider', sa.String(length=8), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('service_user', 'social_provider')
    # ### end Alembic commands ###
