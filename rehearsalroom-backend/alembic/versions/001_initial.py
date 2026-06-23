"""Initial migration - create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(), nullable=False, unique=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])

    # ── refresh_tokens ────────────────────────────────────────────────────────
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token", sa.String(), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_revoked", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_refresh_tokens_token", "refresh_tokens", ["token"])

    # ── bands ─────────────────────────────────────────────────────────────────
    op.create_table(
        "bands",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("genre", sa.String(), nullable=True),
        sa.Column("formed_year", sa.Integer(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── band_members ──────────────────────────────────────────────────────────
    member_role = sa.Enum("band_leader", "member", name="memberrole")
    member_role.create(op.get_bind())
    op.create_table(
        "band_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("band_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bands.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.Enum("band_leader", "member", name="memberrole"), nullable=False),
        sa.Column("instrument", sa.String(), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── invitations ───────────────────────────────────────────────────────────
    invitation_status = sa.Enum("pending", "accepted", "expired", name="invitationstatus")
    invitation_status.create(op.get_bind())
    op.create_table(
        "invitations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("band_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bands.id", ondelete="CASCADE"), nullable=False),
        sa.Column("invited_email", sa.String(), nullable=False),
        sa.Column("invited_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.Enum("pending", "accepted", "expired", name="invitationstatus"), nullable=False),
        sa.Column("token", sa.String(), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_invitations_token", "invitations", ["token"])

    # ── songs ─────────────────────────────────────────────────────────────────
    song_status = sa.Enum("learning", "ready", "on_hold", name="songstatus")
    song_status.create(op.get_bind())
    op.create_table(
        "songs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("band_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bands.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("composer", sa.String(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("status", sa.Enum("learning", "ready", "on_hold", name="songstatus"), nullable=False),
        sa.Column("added_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── rehearsal_sessions ────────────────────────────────────────────────────
    session_status = sa.Enum("upcoming", "ongoing", "completed", "cancelled", name="sessionstatus")
    session_status.create(op.get_bind())
    op.create_table(
        "rehearsal_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("band_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bands.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("status", sa.Enum("upcoming", "ongoing", "completed", "cancelled", name="sessionstatus"), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── session_songs ─────────────────────────────────────────────────────────
    op.create_table(
        "session_songs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rehearsal_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("song_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("songs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False, default=0),
    )

    # ── song_progresses ───────────────────────────────────────────────────────
    op.create_table(
        "song_progresses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rehearsal_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("song_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("songs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("progress_pct", sa.Integer(), nullable=False, default=0),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── feedbacks ─────────────────────────────────────────────────────────────
    op.create_table(
        "feedbacks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rehearsal_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("feedbacks")
    op.drop_table("song_progresses")
    op.drop_table("session_songs")
    op.drop_table("rehearsal_sessions")
    op.drop_table("songs")
    op.drop_table("invitations")
    op.drop_table("band_members")
    op.drop_table("bands")
    op.drop_table("refresh_tokens")
    op.drop_table("users")

    # Drop custom enum types
    sa.Enum(name="sessionstatus").drop(op.get_bind())
    sa.Enum(name="songstatus").drop(op.get_bind())
    sa.Enum(name="invitationstatus").drop(op.get_bind())
    sa.Enum(name="memberrole").drop(op.get_bind())
