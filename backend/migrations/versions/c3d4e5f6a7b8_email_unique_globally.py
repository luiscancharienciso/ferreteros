"""email unique globally

Revision ID: c3d4e5f6a7b8
Revises: 7b242403bdd0
Create Date: 2026-03-13 00:00:00.000000

Cambio: unifica la política de unicidad de email.
- ANTES: UniqueConstraint(tenant_id, email) — único por ferretería.
- DESPUÉS: unique=True en email — único globalmente en la plataforma.

Razón: simplifica el login (no requiere selector de tenant) y es consistente
con el flujo SaaS donde cada persona tiene una sola cuenta en la plataforma.
"""
from alembic import op
import sqlalchemy as sa


revision = 'c3d4e5f6a7b8'
down_revision = '7b242403bdd0'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        # Eliminar constraint compuesto (tenant_id, email)
        batch_op.drop_constraint('uq_user_tenant_email', type_='unique')
        # Crear unique index solo en email
        batch_op.create_index('ix_users_email_unique', ['email'], unique=True)


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index('ix_users_email_unique')
        batch_op.create_unique_constraint('uq_user_tenant_email', ['tenant_id', 'email'])
