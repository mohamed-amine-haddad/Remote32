"""unified_json_session

Revision ID: b571d77229b6
Revises: 
Create Date: 2026-04-25 19:01:17.081916

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b571d77229b6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Drop everything if it exists — safe on both a migrated DB and a fresh one
    for t in ('session', 'device_session', 'application_session', 'board', 'raspberrypi', 'user'):
        conn.execute(sa.text(f"DROP TABLE IF EXISTS {t}"))

    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False, server_default='user'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_user_email', 'user', ['email'], unique=True)

    op.create_table('board',
        sa.Column('serial_number', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='idle'),
        sa.Column('openocd_pid', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('serial_number')
    )

    op.create_table('session',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('json_path', sa.String(), nullable=False),
        sa.Column('target_board_sn', sa.String(), nullable=False),
        sa.Column('control_board_sn', sa.String(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['control_board_sn'], ['board.serial_number']),
        sa.ForeignKeyConstraint(['target_board_sn'], ['board.serial_number']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('session')
    op.drop_table('board')
    op.drop_index('ix_user_email', table_name='user')
    op.drop_table('user')
