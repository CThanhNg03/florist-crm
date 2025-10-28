"""add core business entities

Revision ID: 202403041300
Revises: 202403041200
Create Date: 2024-03-04 13:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "202403041300"
down_revision: Union[str, None] = "202403041200"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


receivemethod_enum = sa.Enum("DELIVERY", "PICKUP", name="receivemethod")
orderstatus_enum = sa.Enum(
    "NEW",
    "CONFIRMING",
    "ASSIGNED",
    "IN_PROGRESS",
    "READY",
    "COMPLETED",
    "CANCELLED",
    name="orderstatus",
)
ordersource_enum = sa.Enum("FORM", "ZALO", "MANUAL", name="ordersource")
paymenttype_enum = sa.Enum("DEPOSIT", "REMAINING", "REFUND", name="paymenttype")
paymentmethod_enum = sa.Enum("CASH", "BANK", "MOMO", "ZALO_PAY", name="paymentmethod")
assignmentstatus_enum = sa.Enum("PENDING", "ACCEPTED", "DONE", name="assignmentstatus")
assignmentrole_enum = sa.Enum("FLORIST", name="assignmentrole")


def upgrade() -> None:
    receivemethod_enum.create(op.get_bind(), checkfirst=True)
    orderstatus_enum.create(op.get_bind(), checkfirst=True)
    ordersource_enum.create(op.get_bind(), checkfirst=True)
    paymenttype_enum.create(op.get_bind(), checkfirst=True)
    paymentmethod_enum.create(op.get_bind(), checkfirst=True)
    assignmentstatus_enum.create(op.get_bind(), checkfirst=True)
    assignmentrole_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("social_link", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone"),
    )
    op.create_index(op.f("ix_customers_phone"), "customers", ["phone"], unique=False)

    op.create_table(
        "skus",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_template", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("unit", sa.Text(), nullable=True),
        sa.Column("track_stock", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("base_price", sa.BigInteger(), nullable=False),
        sa.Column("options_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_skus_code"), "skus", ["code"], unique=False)

    op.create_table(
        "sku_aliases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sku_id", sa.Integer(), nullable=False),
        sa.Column("alias", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["sku_id"], ["skus.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sku_aliases_alias"), "sku_aliases", ["alias"], unique=False)

    op.create_table(
        "sku_bom",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("parent_sku_id", sa.Integer(), nullable=False),
        sa.Column("component_sku_id", sa.Integer(), nullable=False),
        sa.Column("qty", sa.Numeric(12, 3), nullable=False),
        sa.Column("uom", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["component_sku_id"], ["skus.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["parent_sku_id"], ["skus.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("receiver_name", sa.String(length=255), nullable=False),
        sa.Column("receiver_phone", sa.String(length=32), nullable=True),
        sa.Column("receive_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("receive_method", receivemethod_enum, nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("card_message", sa.Text(), nullable=True),
        sa.Column("status", orderstatus_enum, nullable=False),
        sa.Column("source", ordersource_enum, nullable=False),
        sa.Column("total_amount", sa.BigInteger(), server_default=sa.text("0"), nullable=False),
        sa.Column("deposit_amount", sa.BigInteger(), server_default=sa.text("0"), nullable=False),
        sa.Column("remaining_amount", sa.BigInteger(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_orders_code"), "orders", ["code"], unique=False)

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("sku_id", sa.Integer(), nullable=False),
        sa.Column("sku_name_snapshot", sa.String(length=255), nullable=False),
        sa.Column("qty", sa.Numeric(12, 3), nullable=False),
        sa.Column("unit_price", sa.BigInteger(), nullable=False),
        sa.Column("line_total", sa.BigInteger(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("options_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("bom_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sku_id"], ["skus.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("type", paymenttype_enum, nullable=False),
        sa.Column("method", paymentmethod_enum, nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recorded_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recorded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "assignments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("assignee_id", sa.Integer(), nullable=False),
        sa.Column("role", assignmentrole_enum, nullable=False),
        sa.Column("status", assignmentstatus_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["assignee_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("assignments")
    op.drop_table("payments")
    op.drop_table("order_items")
    op.drop_index(op.f("ix_orders_code"), table_name="orders")
    op.drop_table("orders")
    op.drop_table("sku_bom")
    op.drop_index(op.f("ix_sku_aliases_alias"), table_name="sku_aliases")
    op.drop_table("sku_aliases")
    op.drop_index(op.f("ix_skus_code"), table_name="skus")
    op.drop_table("skus")
    op.drop_index(op.f("ix_customers_phone"), table_name="customers")
    op.drop_table("customers")

    assignmentrole_enum.drop(op.get_bind(), checkfirst=True)
    assignmentstatus_enum.drop(op.get_bind(), checkfirst=True)
    paymentmethod_enum.drop(op.get_bind(), checkfirst=True)
    paymenttype_enum.drop(op.get_bind(), checkfirst=True)
    ordersource_enum.drop(op.get_bind(), checkfirst=True)
    orderstatus_enum.drop(op.get_bind(), checkfirst=True)
    receivemethod_enum.drop(op.get_bind(), checkfirst=True)
