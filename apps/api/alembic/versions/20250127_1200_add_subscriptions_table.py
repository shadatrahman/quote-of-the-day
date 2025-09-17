"""Add subscriptions table

Revision ID: f1234567890a
Revises: e987abd5d71f
Create Date: 2025-01-27 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f1234567890a"
down_revision = "e987abd5d71f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create subscription status enum
    op.execute(
        "CREATE TYPE subscriptionstatus AS ENUM ('ACTIVE', 'CANCELLED', 'PAST_DUE', 'INCOMPLETE')"
    )

    # Create subscriptions table
    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "tier",
            sa.Enum("FREE", "PREMIUM", name="subscriptiontier"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "CANCELLED",
                "PAST_DUE",
                "INCOMPLETE",
                name="subscriptionstatus",
            ),
            nullable=False,
        ),
        sa.Column("stripe_customer_id", sa.String(length=255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(length=255), nullable=True),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    # Create indexes for better query performance
    op.create_index(op.f("ix_subscriptions_id"), "subscriptions", ["id"], unique=False)
    op.create_index(
        op.f("ix_subscriptions_user_id"), "subscriptions", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_subscriptions_tier"), "subscriptions", ["tier"], unique=False
    )
    op.create_index(
        op.f("ix_subscriptions_status"), "subscriptions", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_subscriptions_stripe_customer_id"),
        "subscriptions",
        ["stripe_customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscriptions_stripe_subscription_id"),
        "subscriptions",
        ["stripe_subscription_id"],
        unique=False,
    )

    # Create composite indexes
    op.create_index(
        "idx_subscriptions_user_tier",
        "subscriptions",
        ["user_id", "tier"],
        unique=False,
    )
    op.create_index(
        "idx_subscriptions_status_tier",
        "subscriptions",
        ["status", "tier"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop indexes
    op.drop_index("idx_subscriptions_status_tier", table_name="subscriptions")
    op.drop_index("idx_subscriptions_user_tier", table_name="subscriptions")
    op.drop_index(
        op.f("ix_subscriptions_stripe_subscription_id"), table_name="subscriptions"
    )
    op.drop_index(
        op.f("ix_subscriptions_stripe_customer_id"), table_name="subscriptions"
    )
    op.drop_index(op.f("ix_subscriptions_status"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_tier"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_user_id"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_id"), table_name="subscriptions")

    # Drop subscriptions table
    op.drop_table("subscriptions")

    # Drop subscription status enum
    op.execute("DROP TYPE IF EXISTS subscriptionstatus")
