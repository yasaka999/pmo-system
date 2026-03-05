from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.issue import Issue
from app.models.risk import Risk, RISK_MATRIX
from app.schemas.schemas import (
    IssueCreate, IssueUpdate, IssueOut,
    RiskCreate, RiskUpdate, RiskOut,
)
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


# ── 问题台账 ────────────────────────────────────────────
@router.get("/projects/{project_id}/issues", response_model=List[IssueOut])
def list_issues(
    project_id: int,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Issue).filter(Issue.project_id == project_id)
    if status:
        q = q.filter(Issue.status == status)
    if severity:
        q = q.filter(Issue.severity == severity)
    return q.order_by(Issue.raised_date.desc()).all()


@router.post("/projects/{project_id}/issues", response_model=IssueOut, status_code=201)
def create_issue(project_id: int, issue_in: IssueCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    issue = Issue(**{**issue_in.model_dump(), "project_id": project_id})
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@router.put("/issues/{issue_id}", response_model=IssueOut)
def update_issue(issue_id: int, issue_in: IssueUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="问题不存在")
    for k, v in issue_in.model_dump(exclude_unset=True).items():
        setattr(issue, k, v)
    db.commit()
    db.refresh(issue)
    return issue


@router.delete("/issues/{issue_id}", status_code=204)
def delete_issue(issue_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="问题不存在")
    db.delete(issue)
    db.commit()


# ── 风险台账 ────────────────────────────────────────────
@router.get("/projects/{project_id}/risks", response_model=List[RiskOut])
def list_risks(
    project_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Risk).filter(Risk.project_id == project_id)
    if status:
        q = q.filter(Risk.status == status)
    return q.all()


@router.post("/projects/{project_id}/risks", response_model=RiskOut, status_code=201)
def create_risk(project_id: int, risk_in: RiskCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    data = risk_in.model_dump()
    data["project_id"] = project_id
    data["level"] = RISK_MATRIX.get((risk_in.probability, risk_in.impact), "中")
    risk = Risk(**data)
    db.add(risk)
    db.commit()
    db.refresh(risk)
    return risk


@router.put("/risks/{risk_id}", response_model=RiskOut)
def update_risk(risk_id: int, risk_in: RiskUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail="风险不存在")
    update_data = risk_in.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(risk, k, v)
    # 重算风险等级
    prob = update_data.get("probability", risk.probability)
    impact = update_data.get("impact", risk.impact)
    risk.level = RISK_MATRIX.get((prob, impact), "中")
    db.commit()
    db.refresh(risk)
    return risk


@router.delete("/risks/{risk_id}", status_code=204)
def delete_risk(risk_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail="风险不存在")
    db.delete(risk)
    db.commit()
