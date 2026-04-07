"""create messages table

Revision ID: 001
Revises:
Create Date: 2026-04-07
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

message_role = postgresql.ENUM("ai", "user", name="message_role", create_type=False)


def upgrade() -> None:
    message_role.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "messages",
        sa.Column("message_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chat_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("rating", sa.Boolean(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("role", message_role, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("messages")
    message_role.drop(op.get_bind(), checkfirst=True)
