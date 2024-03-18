"""added created_by foreign key

Revision ID: 67dccc64bd1c
Revises: 62371373c321
Create Date: 2024-03-18 09:33:20.141832

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67dccc64bd1c'
down_revision: Union[str, None] = '62371373c321'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.add_column('events', sa.Column('created_by', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_events_created_by', 'events', 'users', ['created_by'], ['id'])


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'events', type_='foreignkey')
    # ### end Alembic commands ###
