from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .questionnaire import QUESTIONNAIRE


class RegisterRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str = Field(min_length=6, max_length=128)
    full_name: str = Field(min_length=1, max_length=120)


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
    new_password: str = Field(min_length=6, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6, max_length=128)


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
    full_name: str | None = None
    age: int | None = Field(default=None, ge=16, le=100)
    occupation: str | None = None
    occupation_detail: str | None = None
    city: str | None = None
    preferred_area: str | None = None
    budget_min: int | None = Field(default=None, ge=0)
    budget_max: int | None = Field(default=None, ge=0)
    move_in_date: str | None = None
    bio: str | None = None
    is_visible: bool | None = None
    photos: list[str] | None = None
    privacy: dict | None = None


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
    score: float
    ml_score: float | None = None
    category_scores: dict[str, float]
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
    description: str | None = None
    city: str
    area: str | None = None
    address: str | None = None
    rent: int = Field(ge=0)
    deposit: int | None = None
    room_type: str = "private"
    bhk: str | None = None
    amenities: list[str] = []
    photos: list[str] = []
    available_from: str | None = None
    looking_for: int | None = None


class ListingUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    area: str | None = None
    address: str | None = None
    rent: int | None = None
    deposit: int | None = None
    room_type: str | None = None
    bhk: str | None = None
    amenities: list[str] | None = None
    photos: list[str] | None = None
    available_from: str | None = None
    looking_for: int | None = None
    is_active: bool | None = None


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
