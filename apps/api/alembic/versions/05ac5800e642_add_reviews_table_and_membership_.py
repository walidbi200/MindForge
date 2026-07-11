"""add_reviews_table_and_membership_position

Revision ID: 05ac5800e642
Revises: bf35be717ff1
Create Date: 2026-07-11 17:43:13.547605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '05ac5800e642'
down_revision: Union[str, Sequence[str], None] = 'bf35be717ff1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()
    if 'reviews' not in existing_tables:
        op.create_table('reviews',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('entity_id', sa.Uuid(), nullable=False),
        sa.Column('entity_type', sa.Enum('CAPTURE', 'CONCEPT', 'SOURCE', name='entitytype'), nullable=False),
        sa.Column('review_type', sa.Enum('READ', 'RECALL', 'FLASHCARD', 'QUIZ', name='reviewtype'), nullable=False),
        sa.Column('status', sa.Enum('NEW', 'LEARNING', 'REVIEWING', 'MASTERED', 'SUSPENDED', name='reviewstatus'), nullable=False),
        sa.Column('difficulty', sa.Enum('VERY_EASY', 'EASY', 'MEDIUM', 'HARD', 'VERY_HARD', name='difficulty'), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('notes', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('next_review_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_reviews_entity_id', 'reviews', ['entity_id'], unique=False)
        op.create_index('ix_reviews_entity_type', 'reviews', ['entity_type'], unique=False)
        op.create_index('ix_reviews_next_review_at', 'reviews', ['next_review_at'], unique=False)
        op.create_index('ix_reviews_status', 'reviews', ['status'], unique=False)
    existing_columns = [col['name'] for col in inspector.get_columns('memberships')]
    if 'position' not in existing_columns:
        op.add_column('memberships', sa.Column('position', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('memberships', 'position')
    op.drop_index('ix_reviews_status', table_name='reviews')
    op.drop_index('ix_reviews_next_review_at', table_name='reviews')
    op.drop_index('ix_reviews_entity_type', table_name='reviews')
    op.drop_index('ix_reviews_entity_id', table_name='reviews')
    op.drop_table('reviews')
