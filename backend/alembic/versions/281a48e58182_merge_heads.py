"""merge heads

Revision ID: 281a48e58182
Revises: add_user_food_history, b70cf50a874d
Create Date: 2025-06-14 13:57:00.454539

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '281a48e58182'
down_revision: Union[str, None] = ('add_user_food_history', 'b70cf50a874d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
