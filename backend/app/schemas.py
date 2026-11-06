from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from .questionnaire import QUESTIONNAIRE


def _clean_urls(urls: list[str] | None, max_items: int) -> list[str] | None:
    """Photos must be our own uploads (/uploads/..) or http(s) URLs; bounded count and length."""
    if urls is None:
        return None
    if len(urls) > max_items:
        raise ValueError(f"At most {max_items} photos")
    out = []
    for u in urls:
        u = (u or "").strip()
        if len(u) > 600 or not (u.startswith(("https://", "http://", "/uploads/"))):
            raise ValueError("Invalid photo URL")
        out.append(u)
    return out


def _clean_tags(tags: list[str] | None, max_items: int = 20, max_len: int = 40) -> list[str] | None:
    if tags is None:
        return None
    cleaned = []
    for t in tags:
        t = (t or "").strip()
        if t and t not in cleaned:
            cleaned.append(t[:max_len])
    return cleaned[:max_items]


class RegisterRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=120)


class DeleteAccountRequest(BaseModel):
    confirm: str  # must be the word DELETE


class LoginRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str


class OtpRequest(BaseModel):
    identifier: str
    purpose: str = "login"


class OtpVerifyRequest(BaseModel):
    identifier: str
    code: str
    purpose: str = "login"


class ForgotPasswordRequest(BaseModel):
    identifier: str


class ResetPasswordRequest(BaseModel):
    identifier: str
    code: str
    new_password: str = Field(min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class VerifyProfileRequest(BaseModel):
    code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str | None = None
    phone: str | None = None
    role: str
    is_active: bool
    is_suspended: bool
    created_at: datetime


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=120)
    age: int | None = Field(default=None, ge=16, le=100)
    occupation: str | None = Field(default=None, max_length=32)
    occupation_detail: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=64)
    preferred_area: str | None = Field(default=None, max_length=120)
    budget_min: int | None = Field(default=None, ge=0, le=10_000_000)
    budget_max: int | None = Field(default=None, ge=0, le=10_000_000)
    move_in_date: str | None = Field(default=None, max_length=32)
    bio: str | None = Field(default=None, max_length=1000)
    is_visible: bool | None = None
    photos: list[str] | None = None
    privacy: dict | None = None

    @field_validator("photos")
    @classmethod
    def _photos(cls, v):
        return _clean_urls(v, 8)

    @field_validator("privacy")
    @classmethod
    def _privacy(cls, v):
        if v is not None and (len(v) > 20 or any(not isinstance(x, bool) for x in v.values())):
            raise ValueError("privacy must map field names to true/false")
        return v


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    full_name: str
    age: int | None = None
    occupation: str | None = None
    occupation_detail: str | None = None
    city: str
    preferred_area: str | None = None
    budget_min: int | None = None
    budget_max: int | None = None
    move_in_date: str | None = None
    bio: str | None = None
    is_verified: bool
    is_visible: bool
    photos: list[str] = []
    privacy: dict = {}
    created_at: datetime
    updated_at: datetime


class QuestionnaireAnswerRequest(BaseModel):
    answers: dict[str, str | int]


class QuestionnaireOut(BaseModel):
    questions: list = QUESTIONNAIRE
    weights: dict = {
        "lifestyle": "30%", "sleep_noise": "20%", "budget_location": "20%",
        "cleanliness": "15%", "routine": "10%", "social": "5%",
    }


class MatchReason(BaseModel):
    category: str
    message: str
    positive: bool


class MatchResult(BaseModel):
    user_id: int
    full_name: str
    age: int | None = None
    occupation: str | None = None
    city: str
    preferred_area: str | None = None
    budget_min: int | None = None
    budget_max: int | None = None
    move_in_date: str | None = None
    bio: str | None = None
    photos: list[str] = []
    is_verified: bool = False
    is_fallback: bool = False
    fallback_note: str | None = None
    score: float | None = None
    ml_score: float | None = None
    category_scores: dict[str, float | None]
    reasons: list[str] = []


class ConnectRequest(BaseModel):
    recipient_id: int


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    connection_id: int
    sender_id: int
    content: str
    is_read: bool
    created_at: datetime


class ConnectionOut(BaseModel):
    id: int
    peer_id: int
    peer_name: str
    status: str
    last_message: str | None = None
    unread_count: int = 0
    created_at: datetime


class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    city: str
    target_area: str | None = None
    budget_min: int | None = None
    budget_max: int | None = None


class GroupInvite(BaseModel):
    user_id: int


class GroupUpdate(BaseModel):
    name: str | None = None
    target_area: str | None = None
    budget_min: int | None = None
    budget_max: int | None = None
    status: str | None = None


class GroupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    owner_id: int
    city: str
    target_area: str | None = None
    budget_min: int | None = None
    budget_max: int | None = None
    status: str
    created_at: datetime
    members: list[dict] = []


class ListingCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    city: str = Field(min_length=1, max_length=64)
    area: str | None = Field(default=None, max_length=120)
    address: str | None = Field(default=None, max_length=500)
    rent: int = Field(ge=0, le=10_000_000)
    deposit: int | None = Field(default=None, ge=0, le=100_000_000)
    room_type: str = Field(default="private", max_length=32)
    bhk: str | None = Field(default=None, max_length=16)
    amenities: list[str] = []
    photos: list[str] = []
    available_from: str | None = Field(default=None, max_length=32)
    looking_for: int | None = Field(default=None, ge=0, le=20)

    @field_validator("amenities")
    @classmethod
    def _amenities(cls, v):
        return _clean_tags(v)

    @field_validator("photos")
    @classmethod
    def _photos(cls, v):
        return _clean_urls(v, 10)


class ListingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    area: str | None = Field(default=None, max_length=120)
    address: str | None = Field(default=None, max_length=500)
    rent: int | None = Field(default=None, ge=0, le=10_000_000)
    deposit: int | None = Field(default=None, ge=0, le=100_000_000)
    room_type: str | None = Field(default=None, max_length=32)
    bhk: str | None = Field(default=None, max_length=16)
    amenities: list[str] | None = None
    photos: list[str] | None = None
    available_from: str | None = Field(default=None, max_length=32)
    looking_for: int | None = Field(default=None, ge=0, le=20)
    is_active: bool | None = None

    @field_validator("amenities")
    @classmethod
    def _amenities(cls, v):
        return _clean_tags(v)

    @field_validator("photos")
    @classmethod
    def _photos(cls, v):
        return _clean_urls(v, 10)


class ListingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    title: str
    description: str | None = None
    city: str
    area: str | None = None
    address: str | None = None
    rent: int
    deposit: int | None = None
    room_type: str
    bhk: str | None = None
    amenities: list[str] = []
    photos: list[str] = []
    available_from: str | None = None
    looking_for: int | None = None
    is_verified: bool
    is_active: bool
    status: str
    created_at: datetime
    owner_name: str | None = None
    residents: list["ResidentOut"] = []


class ResidentOut(BaseModel):
    """A current resident of a listing, shown to people browsing it."""
    id: int  # listing_resident row id
    user_id: int
    status: str  # pending | accepted (pending only shown to the poster)
    full_name: str
    age: int | None = None
    occupation: str | None = None
    occupation_detail: str | None = None
    bio: str | None = None
    photos: list[str] = []
    is_verified: bool = False
    score: float | None = None  # compatibility with the viewer, if both have a questionnaire
    reasons: list[str] = []
    is_you: bool = False


class ResidentAdd(BaseModel):
    identifier: str = Field(min_length=3, max_length=255)  # email or phone of a registered user


class ResidentInvitation(BaseModel):
    id: int
    listing_id: int
    listing_title: str
    city: str
    area: str | None = None
    invited_by: str | None = None


ListingOut.model_rebuild()


class ReportCreate(BaseModel):
    target_type: str  # user | listing
    target_user_id: int | None = None
    listing_id: int | None = None
    reason: str = Field(min_length=3, max_length=64)
    details: str | None = None


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reporter_id: int
    target_user_id: int | None = None
    listing_id: int | None = None
    target_type: str
    reason: str
    details: str | None = None
    severity: str
    status: str
    created_at: datetime
    resolved_at: datetime | None = None


class BlockRequest(BaseModel):
    user_id: int


class ReviewReportRequest(BaseModel):
    action: str  # resolve | dismiss | suspend_user
