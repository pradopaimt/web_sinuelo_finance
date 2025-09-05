"""add dre, ir_eduardo, ir_roberto to lancamento

Revision ID: add_dre_ir_columns
Revises: <coloque_aqui_o_id_da_última_revision>
Create Date: 2025-09-05
"""

from alembic import op
import sqlalchemy as sa


# IDs de revisão (atualize conforme sua sequência)
revision = 'add_dre_ir_columns'
down_revision = '<coloque_aqui_o_id_da_última_revision>'
branch_labels = None
depends_on = None

# IDs de revisão
revision = 'a1b2c3d4e5f6'      
down_revision = '8634ce8fd1fc' 
branch_labels = None
depends_on = None

def upgrade():
    # adiciona colunas novas
    op.add_column('lancamento', sa.Column('dre', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column('lancamento', sa.Column('ir_eduardo', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column('lancamento', sa.Column('ir_roberto', sa.Boolean(), server_default=sa.false(), nullable=False))

    # se a coluna antiga "ir" ainda existir, pode remover
    try:
        op.drop_column('lancamento', 'ir')
    except Exception:
        pass  # ignora se já não existir


def downgrade():
    # recria a coluna antiga "ir"
    op.add_column('lancamento', sa.Column('ir', sa.Boolean(), server_default=sa.false(), nullable=False))

    # remove as novas colunas
    op.drop_column('lancamento', 'dre')
    op.drop_column('lancamento', 'ir_eduardo')
    op.drop_column('lancamento', 'ir_roberto')
