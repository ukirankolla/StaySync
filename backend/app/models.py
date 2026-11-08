from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True, index=True, nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(16), default="user")  # user | admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    profile: Mapped["Profile | None"] = relationship(back_populates="user", uselist=False,
                                                     cascade="all, delete-orphan")
    questionnaire: Mapped["Questionnaire | None"] = relationship(back_populates="user", uselist=False,
                                                                 cascade="all, delete-orphan")



class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    occupation: Mapped[str] = mapped_column(String(32), default="other")  # student | professional | other
    occupation_detail: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(64))
    preferred_area: Mapped[str | None] = mapped_column(String(120), nullable=True)
    budget_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    budget_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    move_in_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    photos: Mapped[list] = mapped_column(JSON, default=list)
    privacy: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    user: Mapped[User] = relationship(back_populates="profile")


class Questionnaire(Base):
    __tablename__ = "questionnaires"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    answers: Mapped[dict] = mapped_column(JSON, default=dict)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    user: Mapped[User] = relationship(back_populates="questionnaire")


class Connection(Base):
    __tablename__ = "connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending | accepted | declined
    score_at_connect: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


group_members = Table(
    "group_members",
    Base.metadata,
    Column("group_id", ForeignKey("room_groups.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("joined_at", DateTime, default=utcnow),
)


class RoomGroup(Base):
    __tablename__ = "room_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    city: Mapped[str] = mapped_column(String(64))
    target_area: Mapped[str | None] = mapped_column(String(120), nullable=True)
    budget_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    budget_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="active")  # active | housed | disbanded
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    members: Mapped[list[User]] = relationship(secondary=group_members)


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(String(64), index=True)
    area: Mapped[str | None] = mapped_column(String(120), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    rent: Mapped[int] = mapped_column(Integer)
    deposit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    room_type: Mapped[str] = mapped_column(String(32), default="private")  # private | shared | whole
    bhk: Mapped[str | None] = mapped_column(String(16), nullable=True)
    amenities: Mapped[list] = mapped_column(JSON, default=list)
    photos: Mapped[list] = mapped_column(JSON, default=list)
    available_from: Mapped[str | None] = mapped_column(String(32), nullable=True)
    looking_for: Mapped[int | None] = mapped_column(Integer, nullable=True)  # no. of flatmates wanted
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending | approved | rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class ListingResident(Base):
    """A person who already lives in the listed room/flat (added by the poster, confirmed by them)."""
    __tablename__ = "listing_residents"
    __table_args__ = (UniqueConstraint("listing_id", "user_id", name="uq_listing_resident"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending | accepted | declined
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    connection_id: Mapped[int] = mapped_column(ForeignKey("connections.id"), index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    target_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    listing_id: Mapped[int | None] = mapped_column(ForeignKey("listings.id"), nullable=True, index=True)
    target_type: Mapped[str] = mapped_column(String(16))  # user | listing | message
    reason: Mapped[str] = mapped_column(String(64))
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(16), default="low")  # low | medium | high
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending | resolved | dismissed
    resolved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Block(Base):
    __tablename__ = "blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    blocker_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    blocked_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class OtpCode(Base):
    __tablename__ = "otp_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    identifier: Mapped[str] = mapped_column(String(255), index=True)  # email or phone
    code: Mapped[str] = mapped_column(String(8))
    purpose: Mapped[str] = mapped_column(String(16), default="login")
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(48), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class MatchFeedback(Base):
    """Outcome feedback after two people connect (deck: measure outcomes, not downloads)."""
    __tablename__ = "match_feedback"
    __table_args__ = (UniqueConstraint("user_id", "connection_id", name="uq_feedback_user_conn"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    connection_id: Mapped[int] = mapped_column(ForeignKey("connections.id", ondelete="CASCADE"), index=True)
    fits: Mapped[bool] = mapped_column(Boolean)  # did the suggested match fit my preferences?
    outcome: Mapped[str] = mapped_column(String(24), default="talking")
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Hostel(Base):
    """A college / hostel / PG operator running shared-room allocation on StaySync."""
    __tablename__ = "hostels"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    institution: Mapped[str | None] = mapped_column(String(160), nullable=True)
    join_code: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    room_size: Mapped[int] = mapped_column(Integer, default=2)
    allocation_final: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class HostelMember(Base):
    __tablename__ = "hostel_members"
    __table_args__ = (UniqueConstraint("hostel_id", "user_id", name="uq_hostel_member"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hostel_id: Mapped[int] = mapped_column(ForeignKey("hostels.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    block: Mapped[str] = mapped_column(String(80), default="General")  # hostel/gender policy group
    special_request: Mapped[str | None] = mapped_column(Text, nullable=True)  # accessibility etc.
    room_no: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="intake")  # intake | suggested | approved
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class HostelChangeRequest(Base):
    __tablename__ = "hostel_change_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hostel_id: Mapped[int] = mapped_column(ForeignKey("hostels.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending | approved | declined
    staff_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class MatchMark(Base):
    """A member saved (bookmarked) or skipped someone in Discover."""
    __tablename__ = "match_marks"
    __table_args__ = (UniqueConstraint("user_id", "target_id", name="uq_match_mark"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    target_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(8), default="saved")  # saved | skipped
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class GroupRule(Base):
    """A house rule the members of a roommate group agree on."""
    __tablename__ = "group_rules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("room_groups.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(String(200))
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class RoommateReview(Base):
    """Review of someone you actually connected and chatted with (one per connection and reviewer)."""
    __tablename__ = "roommate_reviews"
    __table_args__ = (UniqueConstraint("reviewer_id", "connection_id", name="uq_review_reviewer_conn"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    reviewee_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    connection_id: Mapped[int] = mapped_column(ForeignKey("connections.id", ondelete="CASCADE"), index=True)
    rating: Mapped[int] = mapped_column(Integer)
    would_live_again: Mapped[bool] = mapped_column(Boolean, default=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
