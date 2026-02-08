"""Initial migration: create tasks, events, and reminders tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-08 19:16:37.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create event table
    op.create_table(
        'event',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('start_at', sa.DateTime(), nullable=False),
        sa.Column('end_at', sa.DateTime(), nullable=True),
        sa.Column('all_day', sa.Boolean(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create task table
    op.create_table(
        'task',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.Column('timing_relative_to_event', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create reminder table
    op.create_table(
        'reminder',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('trigger_at', sa.DateTime(), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('reminder')
    op.drop_table('task')
    op.drop_table('event')
