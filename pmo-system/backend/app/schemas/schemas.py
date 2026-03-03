from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, EmailStr


# ============ SysDict Schemas ============

class SysDictBase(BaseModel):
    category: str
    code: str
    label: str
    sort_order: int = 0
    color: Optional[str] = None
    is_active: bool = True

class SysDictCreate(SysDictBase):
    pass

class SysDictUpdate(BaseModel):
    category: Optional[str] = None
    code: Optional[str] = None
    label: Optional[str] = None
    sort_order: Optional[int] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None

class SysDictOut(SysDictBase):
    id: int
    class Config:
        from_attributes = True

# ============ User Schemas ============

class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: str = "member"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ============ Project Schemas ============

class ProjectBase(BaseModel):
    code: str
    name: str
    client: Optional[str] = None
    manager: Optional[str] = None
    phase: str = "启动"
    status: str = "正常"
    plan_start: Optional[date] = None
    plan_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    budget_mandays: float = 0
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    client: Optional[str] = None
    manager: Optional[str] = None
    phase: Optional[str] = None
    status: Optional[str] = None
    plan_start: Optional[date] = None
    plan_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    budget_mandays: Optional[float] = None
    description: Optional[str] = None

class ProjectOut(ProjectBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class ProjectSummary(BaseModel):
    id: int
    code: str
    name: str
    client: Optional[str] = None
    manager: Optional[str] = None
    phase: str
    status: str
    plan_end: Optional[date] = None
    milestone_count: int = 0
    open_issue_count: int = 0
    open_risk_count: int = 0
    used_mandays: float = 0
    budget_mandays: float = 0
    created_by: Optional[int] = None
    class Config:
        from_attributes = True



# ============ Milestone Schemas ============

class MilestoneBase(BaseModel):
    name: str
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    status: str = "未开始"
    description: Optional[str] = None
    order_index: int = 0

class MilestoneCreate(MilestoneBase):
    project_id: int

class MilestoneUpdate(BaseModel):
    name: Optional[str] = None
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    status: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None

class MilestoneOut(MilestoneBase):
    id: int
    project_id: int
    created_at: datetime
    class Config:
        from_attributes = True


# ============ Task Schemas ============

class TaskBase(BaseModel):
    name: str
    milestone_id: Optional[int] = None
    assignee: Optional[str] = None
    plan_start: Optional[date] = None
    plan_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    progress: int = 0
    status: str = "未开始"
    notes: Optional[str] = None

class TaskCreate(TaskBase):
    project_id: int

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    milestone_id: Optional[int] = None
    assignee: Optional[str] = None
    plan_start: Optional[date] = None
    plan_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    progress: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class TaskOut(TaskBase):
    id: int
    project_id: int
    created_at: datetime
    class Config:
        from_attributes = True


# ============ Issue Schemas ============

class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "中"
    source: str = "内部"
    assignee: Optional[str] = None
    raised_date: Optional[date] = None
    due_date: Optional[date] = None
    resolved_date: Optional[date] = None
    status: str = "待处理"
    resolution: Optional[str] = None

class IssueCreate(IssueBase):
    project_id: int

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    source: Optional[str] = None
    assignee: Optional[str] = None
    raised_date: Optional[date] = None
    due_date: Optional[date] = None
    resolved_date: Optional[date] = None
    status: Optional[str] = None
    resolution: Optional[str] = None

class IssueOut(IssueBase):
    id: int
    project_id: int
    created_at: datetime
    class Config:
        from_attributes = True


# ============ Risk Schemas ============

class RiskBase(BaseModel):
    title: str
    description: Optional[str] = None
    probability: str = "中"
    impact: str = "中"
    mitigation: Optional[str] = None
    assignee: Optional[str] = None
    status: str = "开放"

class RiskCreate(RiskBase):
    project_id: int

class RiskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    probability: Optional[str] = None
    impact: Optional[str] = None
    mitigation: Optional[str] = None
    assignee: Optional[str] = None
    status: Optional[str] = None

class RiskOut(RiskBase):
    id: int
    project_id: int
    level: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True


# ============ ManDay Schemas ============

class ManDayBase(BaseModel):
    staff_name: str
    role: Optional[str] = None
    work_date: date
    days: float
    work_content: Optional[str] = None
    is_billable: bool = True

class ManDayCreate(ManDayBase):
    project_id: int

class ManDayUpdate(BaseModel):
    staff_name: Optional[str] = None
    role: Optional[str] = None
    work_date: Optional[date] = None
    days: Optional[float] = None
    work_content: Optional[str] = None
    is_billable: Optional[bool] = None

class ManDayOut(ManDayBase):
    id: int
    project_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ManDayStat(BaseModel):
    project_id: int
    project_name: str
    total_days: float
    billable_days: float
    staff_breakdown: List[dict] = []
