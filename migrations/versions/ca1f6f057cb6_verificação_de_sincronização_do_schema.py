"""Verificação de sincronização do schema

Revision ID: ca1f6f057cb6
Revises: f5af6ea50c9b
Create Date: 2025-05-26 06:04:40.234075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca1f6f057cb6'
down_revision: Union[str, None] = 'f5af6ea50c9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('clients', sa.Column('numero_whatsapp', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('clients', 'numero_whatsapp')
    # ### end Alembic commands ###
