"""add user foreing key to device/application session

Revision ID: 50e3fa7c6b2c
Revises: e41bae78d6d7
Create Date: 2026-04-21 16:19:41.678427

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50e3fa7c6b2c'
down_revision: Union[str, Sequence[str], None] = 'e41bae78d6d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('application_session') as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_application_session_user', 'user', ['user_id'], ['id'])

    with op.batch_alter_table('device_session') as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_device_session_user', 'user', ['user_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('device_session') as batch_op:
        batch_op.drop_constraint('fk_device_session_user', type_='foreignkey')
        batch_op.drop_column('user_id')

    with op.batch_alter_table('application_session') as batch_op:
        batch_op.drop_constraint('fk_application_session_user', type_='foreignkey')
        batch_op.drop_column('user_id')
