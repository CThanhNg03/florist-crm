"""add tasks and florists"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "202406010000_add_tasks_and_florists"
down_revision = "202403041300"
branch_labels = None
depends_on = None


def upgrade() -> None:
    floristrole = sa.Enum("FLORIST", "LEAD", "ADMIN", name="floristrole")
    floristrole.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "florists",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("role", floristrole, nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    crmorderstatus = sa.Enum("NEW", "CONFIRMED", "IN_PROGRESS", "COMPLETED", "CANCELLED", name="crmorderstatus")
    crmorderstatus.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "crm_orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_name", sa.String(length=255), nullable=False),
        sa.Column("customer_phone", sa.String(length=32), nullable=False),
        sa.Column("receiver_name", sa.String(length=255), nullable=False),
        sa.Column("receiver_phone", sa.String(length=32), nullable=True),
        sa.Column("delivery_address", sa.Text(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", crmorderstatus, nullable=False),
        sa.Column("pricing", sa.BigInteger(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    taskstatus = sa.Enum("PENDING", "ASSIGNED", "IN_PROGRESS", "COMPLETED", "CANCELLED", name="taskstatus")
    taskstatus.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=True),
        sa.Column("florist_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", taskstatus, nullable=False),
        sa.Column("schedule", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pricing", sa.BigInteger(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("photos", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("completion_proof_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["florist_id"], ["florists.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["order_id"], ["crm_orders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("tasks")
    op.drop_table("crm_orders")
    op.drop_table("florists")

    op.execute("DROP TYPE IF EXISTS taskstatus")
    op.execute("DROP TYPE IF EXISTS crmorderstatus")
    op.execute("DROP TYPE IF EXISTS floristrole")
