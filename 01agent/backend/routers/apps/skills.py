from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select, and_
from db.database import get_session
from db.models import User, Skill
from dependencies.auth_dependencies import get_current_user_dependency
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(
    prefix='/skills',
    tags=['skills'],
    dependencies=[Depends(get_current_user_dependency)]
)

class SkillCreate(BaseModel):
    name: str
    description: str
    instructions: str
    is_public: bool = False

@router.post('', response_model=Skill)
async def create_skill(skill_data: SkillCreate,
                       db: Session = Depends(get_session),
                       user: User = Depends(get_current_user_dependency)):
    skill = Skill(
        name=skill_data.name,
        description=skill_data.description,
        instructions=skill_data.instructions,
        author_id=user.id,
        is_public=skill_data.is_public
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill

@router.get('', response_model=List[Skill])
async def list_skills(public_only: bool = True,
                      db: Session = Depends(get_session),
                      user: User = Depends(get_current_user_dependency)):
    if public_only:
        statement = select(Skill).where(Skill.is_public == True)
    else:
        statement = select(Skill).where(and_(Skill.author_id == user.id))

    return db.exec(statement).all()

@router.get('/marketplace', response_model=List[Skill])
async def marketplace(db: Session = Depends(get_session)):
    statement = select(Skill).where(Skill.is_public == True).order_by(Skill.usage_count.desc()).limit(50)
    return db.exec(statement).all()
