from fastapi import APIRouter
from sqlmodel import select
from config.db_connection import SessionDep

from utils.models import Plan

router = APIRouter()

@router.post("/plans", tags=["Plans"])
async def create_plan(plan_data: Plan, session: SessionDep):
  plan_db = Plan.model_validate(plan_data.model_dump())
  session.add(plan_db)
  session.commit()
  session.refresh(plan_db)
  return plan_db

@router.get("/plans", response_model=list[Plan], tags=["Plans"])
async def list_plans(session: SessionDep):
  plans = session.exec(select(Plan)).all()
  return plans
