from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from pydantic import BaseModel, Field

from ..models import Block, GroupRule, Profile, RoomGroup, User, group_members
from ..schemas import GroupCreate, GroupInvite, GroupOut, GroupUpdate
from ..services.events import track

router = APIRouter(prefix="/groups", tags=["groups"])


def _group_out(db: Session, group: RoomGroup) -> GroupOut:
    members = []
    for member in group.members:
        p = db.query(Profile).filter(Profile.user_id == member.id).first()
        members.append({"user_id": member.id, "full_name": p.full_name if p else "User",
                        "is_owner": group.owner_id == member.id})
    return GroupOut(
        id=group.id, name=group.name, owner_id=group.owner_id, city=group.city,
        target_area=group.target_area, budget_min=group.budget_min, budget_max=group.budget_max,
        status=group.status, created_at=group.created_at, members=members,
        rules=[{"id": r.id, "text": r.text} for r in db.query(GroupRule).filter(GroupRule.group_id == group.id)
               .order_by(GroupRule.id).all()],
    )


@router.post("", response_model=GroupOut)
def create_group(payload: GroupCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    group = RoomGroup(name=payload.name, owner_id=user.id, city=payload.city,
                      target_area=payload.target_area, budget_min=payload.budget_min,
                      budget_max=payload.budget_max)
    db.add(group)
    db.flush()
    db.execute(group_members.insert().values(group_id=group.id, user_id=user.id))
    db.commit()
    db.refresh(group)
    track(db, user.id, "group_created", {"group_id": group.id})
    return _group_out(db, group)


@router.get("", response_model=list[GroupOut])
def list_my_groups(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    groups = db.query(RoomGroup).join(group_members, group_members.c.group_id == RoomGroup.id).filter(
        group_members.c.user_id == user.id).all()
    return [_group_out(db, g) for g in groups]


@router.get("/{group_id}", response_model=GroupOut)
def get_group(group_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    group = db.get(RoomGroup, group_id)
    if not group or user.id not in {m.id for m in group.members}:
        # members only: a group lists its members' names, budget and target area
        raise HTTPException(status_code=404, detail="Group not found")
    return _group_out(db, group)


@router.post("/{group_id}/invite")
def invite_to_group(group_id: int, payload: GroupInvite, user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    group = db.get(RoomGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the group owner can invite")
    target = db.get(User, payload.user_id)
    if not target or not target.is_active or target.is_suspended:
        raise HTTPException(status_code=404, detail="User not found")
    if db.query(Block.id).filter(
        ((Block.blocker_id == user.id) & (Block.blocked_id == target.id))
        | ((Block.blocker_id == target.id) & (Block.blocked_id == user.id))
    ).first():
        raise HTTPException(status_code=400, detail="You can't invite this user")
    member_ids = {m.id for m in group.members}
    if payload.user_id in member_ids:
        raise HTTPException(status_code=409, detail="Already a member")
    db.execute(group_members.insert().values(group_id=group.id, user_id=payload.user_id))
    db.commit()
    track(db, user.id, "group_invite", {"group_id": group_id, "invitee": payload.user_id})
    return _group_out(db, group)


@router.delete("/{group_id}/members/{user_id}")
def remove_member(group_id: int, user_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    group = db.get(RoomGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.owner_id != user.id and user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    db.execute(group_members.delete().where(group_members.c.group_id == group_id,
                                            group_members.c.user_id == user_id))
    db.commit()
    return _group_out(db, group)


@router.put("/{group_id}", response_model=GroupOut)
def update_group(group_id: int, payload: GroupUpdate, user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    group = db.get(RoomGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the owner can edit")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(group, field, value)
    db.commit()
    db.refresh(group)
    return _group_out(db, group)


class RuleIn(BaseModel):
    text: str = Field(min_length=3, max_length=200)


def _member_group(db: Session, user: User, group_id: int) -> RoomGroup:
    group = db.get(RoomGroup, group_id)
    if not group or user.id not in {m.id for m in group.members}:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.post("/{group_id}/rules", response_model=GroupOut)
def add_rule(group_id: int, payload: RuleIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Any member can propose a house rule (e.g. 'Guests allowed till 10 PM')."""
    group = _member_group(db, user, group_id)
    if db.query(GroupRule).filter(GroupRule.group_id == group.id).count() >= 20:
        raise HTTPException(status_code=400, detail="A group can have at most 20 house rules.")
    db.add(GroupRule(group_id=group.id, text=payload.text.strip(), created_by=user.id))
    db.commit()
    return _group_out(db, group)


@router.delete("/{group_id}/rules/{rule_id}", response_model=GroupOut)
def delete_rule(group_id: int, rule_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    group = _member_group(db, user, group_id)
    db.query(GroupRule).filter(GroupRule.id == rule_id, GroupRule.group_id == group.id).delete()
    db.commit()
    return _group_out(db, group)
