"""Add users table

Revision ID: e987abd5d71f
Revises:
Create Date: 2025-09-17 22:50:06.556487

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e987abd5d71f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column(
            "subscription_tier",
            sa.Enum("FREE", "PREMIUM", name="subscriptiontier"),
            nullable=False,
        ),
        sa.Column("timezone", sa.String(length=50), nullable=False),
        sa.Column("notification_settings", sa.JSON(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_quote_delivered", sa.DateTime(timezone=True), nullable=True),
        sa.Column("email_verification_token", sa.String(length=255), nullable=True),
        sa.Column(
            "email_verification_expires_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column("password_reset_token", sa.String(length=255), nullable=True),
        sa.Column(
            "password_reset_expires_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop indexes
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")

    # Drop users table
    op.drop_table("users")

    # Drop enum type
    op.execute("DROP TYPE IF EXISTS subscriptiontier")
