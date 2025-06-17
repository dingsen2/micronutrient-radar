"""add user food history

Revision ID: add_user_food_history
Revises: f7c4486656eb
Create Date: 2024-03-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_user_food_history'
down_revision = 'f7c4486656eb'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create user_food_history table
    op.create_table('user_food_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('meal_datetime', sa.DateTime(), nullable=False),
        sa.Column('meal_type', sa.String(20), nullable=False),
        sa.Column('food_image_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('total_nutrients', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['food_image_id'], ['food_images.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_meal_datetime', 'user_food_history', ['user_id', 'meal_datetime'], unique=False)

def downgrade() -> None:
    op.drop_index('idx_user_meal_datetime', table_name='user_food_history')
    op.drop_table('user_food_history') 