"""Add login fields and refresh tokens

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add login-related fields to providers table
    op.add_column('providers', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))
    op.add_column('providers', sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('providers', sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))
    op.add_column('providers', sa.Column('login_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Create refresh_tokens table
    op.create_table('refresh_tokens',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('provider_id', UUID(as_uuid=True), sa.ForeignKey('providers.id'), nullable=False),
        sa.Column('token_hash', sa.Text(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes
    op.create_index('ix_refresh_tokens_provider_id', 'refresh_tokens', ['provider_id'])
    op.create_index('ix_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'])
    op.create_index('ix_refresh_tokens_expires_at', 'refresh_tokens', ['expires_at'])
    op.create_index('ix_refresh_tokens_is_revoked', 'refresh_tokens', ['is_revoked'])


def downgrade() -> None:
    # Drop refresh_tokens table
    op.drop_index('ix_refresh_tokens_is_revoked', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_expires_at', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_token_hash', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_provider_id', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    
    # Remove login-related fields from providers table
    op.drop_column('providers', 'login_count')
    op.drop_column('providers', 'locked_until')
    op.drop_column('providers', 'failed_login_attempts')
    op.drop_column('providers', 'last_login')
