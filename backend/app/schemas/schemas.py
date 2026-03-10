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
    phase: str = "ph_kickoff"  # ph_pre=售前，ph_kickoff=启动，ph_impl=实施，ph_accept=验收，ph_close=收尾
    status: str = "st_normal"  # st_normal=正常，st_warn=预警，st_delay=延期，st_pause=暂停，st_done=已完成
    plan_start: Optional[date] = None
    plan_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    budget_mandays: float = 0
    description: Optional[str] = None
    contract_no: Optional[str] = None
    region: Optional[str] = None
    plan_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    plan_initial_acceptance_date: Optional[date] = None
    actual_initial_acceptance_date: Optional[date] = None
    plan_final_acceptance_date: Optional[date] = None
    actual_final_acceptance_date: Optional[date] = None

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
    contract_no: Optional[str] = None
    region: Optional[str] = None
    plan_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    plan_initial_acceptance_date: Optional[date] = None
    actual_initial_acceptance_date: Optional[date] = None
    plan_final_acceptance_date: Optional[date] = None
    actual_final_acceptance_date: Optional[date] = None

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
    plan_start: Optional[date] = None
    plan_end: Optional[date] = None
    milestone_count: int = 0
    open_issue_count: int = 0
    open_risk_count: int = 0
    used_mandays: float = 0
    budget_mandays: float = 0
    created_by: Optional[int] = None
    # 合同 & 区域
    contract_no: Optional[str] = None
    region: Optional[str] = None
    # 交付 & 验收日期
    plan_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    plan_initial_acceptance_date: Optional[date] = None
    actual_initial_acceptance_date: Optional[date] = None
    plan_final_acceptance_date: Optional[date] = None
    actual_final_acceptance_date: Optional[date] = None
    class Config:
        from_attributes = True



# ============ Milestone Schemas ============

class MilestoneBase(BaseModel):
    name: str
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    status: str = "ms_notstart"  # ms_notstart=未开始，ms_inprog=进行中，ms_done=已完成，ms_delay=延期
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
    status: str = "ms_notstart"  # ms_notstart=未开始，ms_inprog=进行中，ms_done=已完成，ms_delay=延期
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
    severity: str = "isev_m"  # isev_h=高，isev_m=中，isev_l=低
    source: str = "src_inter"  # src_client=客户，src_inter=内部，src_3rd=第三方
    assignee: Optional[str] = None
    raised_date: Optional[date] = None
    due_date: Optional[date] = None
    resolved_date: Optional[date] = None
    status: str = "ist_open"  # ist_open=待处理，ist_doing=处理中，ist_closed=已关闭
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
    probability: str = "rp_m"  # rp_h=高，rp_m=中，rp_l=低
    impact: str = "ri_m"  # ri_h=高，ri_m=中，ri_l=低
    mitigation: Optional[str] = None
    assignee: Optional[str] = None
    status: str = "rs_open"  # rs_open=开放，rs_mitig=已缓解，rs_closed=已关闭

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

# ============ Batch Operations ============
class SysDictBatchItem(BaseModel):
    id: Optional[int] = None  # None for new items
    category: str
    code: str
    label: str
    sort_order: int = 0
    color: Optional[str] = None
    is_active: bool = True
    deleted: Optional[bool] = None  # Mark for deletion (accepts _deleted from frontend)
    
    model_config = {
        'populate_by_name': True,
        'extra': 'allow'  # Allow extra fields like _deleted
    }

class SysDictBatchSave(BaseModel):
    items: List[SysDictBatchItem]


# ============ Operation Log Schemas ============
class OperationLogBase(BaseModel):
    action: str
    module: Optional[str] = None
    description: Optional[str] = None
    request_method: Optional[str] = None
    request_url: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class OperationLogCreate(OperationLogBase):
    user_id: Optional[int] = None
    username: Optional[str] = None

class OperationLogOut(OperationLogBase):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
