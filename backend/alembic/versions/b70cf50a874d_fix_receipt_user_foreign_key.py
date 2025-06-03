"""fix receipt user foreign key

Revision ID: b70cf50a874d
Revises: f7c4486656eb
Create Date: 2025-06-03 10:06:50.782717

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b70cf50a874d'
down_revision: Union[str, None] = 'f7c4486656eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop foreign key constraints first
    op.drop_constraint('receipt_user_id_fkey', 'receipt', type_='foreignkey')
    op.drop_constraint('nutrientledger_user_id_fkey', 'nutrientledger', type_='foreignkey')
    
    # Rename the user table to users
    op.rename_table('user', 'users')
    
    # Recreate foreign key constraints with the new table name
    op.create_foreign_key(
        'receipt_user_id_fkey',
        'receipt', 'users',
        ['user_id'], ['id']
    )
    op.create_foreign_key(
        'nutrientledger_user_id_fkey',
        'nutrientledger', 'users',
        ['user_id'], ['id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop foreign key constraints
    op.drop_constraint('receipt_user_id_fkey', 'receipt', type_='foreignkey')
    op.drop_constraint('nutrientledger_user_id_fkey', 'nutrientledger', type_='foreignkey')
    
    # Rename the users table back to user
    op.rename_table('users', 'user')
    
    # Recreate foreign key constraints with the original table name
    op.create_foreign_key(
        'receipt_user_id_fkey',
        'receipt', 'user',
        ['user_id'], ['id']
    )
    op.create_foreign_key(
        'nutrientledger_user_id_fkey',
        'nutrientledger', 'user',
        ['user_id'], ['id']
    )
