"""
报告下载 API
- 所有中文文件名使用 urllib.parse.quote 编码到 RFC 5987 格式，避免 latin-1 编码失败
"""
from datetime import date
from typing import Optional
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
import io

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.report_service import (
    generate_weekly_report,
    generate_monthly_report,
    generate_issue_risk_excel,
    generate_manday_excel,
    generate_status_excel,
    generate_portfolio_report_word,
    generate_portfolio_excel,
)

router = APIRouter()

WORD_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _disposition(filename: str) -> str:
    """生成兼容中文文件名的 Content-Disposition 头值（RFC 5987）"""
    encoded = quote(filename, encoding="utf-8")
    return f"attachment; filename*=UTF-8''{encoded}"


@router.get("/projects/{project_id}/reports/weekly")
def weekly_report(
    project_id: int,
    report_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """下载项目周报（Word格式）"""
    try:
        data = generate_weekly_report(project_id, db, report_date)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败：{str(e)}")

    filename = f"周报_{report_date or date.today()}.docx"
    return Response(
        content=data,
        media_type=WORD_MIME,
        headers={"Content-Disposition": _disposition(filename)},
    )


@router.get("/projects/{project_id}/reports/monthly")
def monthly_report(
    project_id: int,
    year: int,
    month: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """下载项目月报（Word格式）"""
    try:
        data = generate_monthly_report(project_id, year, month, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败：{str(e)}")

    filename = f"月报_{year}{month:02d}.docx"
    return Response(
        content=data,
        media_type=WORD_MIME,
        headers={"Content-Disposition": _disposition(filename)},
    )


@router.get("/projects/{project_id}/reports/issues-risks")
def issue_risk_report(
    project_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """下载问题与风险台账（Excel格式）"""
    try:
        data = generate_issue_risk_excel(project_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败：{str(e)}")

    return Response(
        content=data,
        media_type=EXCEL_MIME,
        headers={"Content-Disposition": _disposition("问题风险台账.xlsx")},
    )


@router.get("/projects/{project_id}/reports/mandays")
def manday_report(
    project_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """下载人天统计报表（Excel格式）"""
    try:
        data = generate_manday_excel(project_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败：{str(e)}")

    return Response(
        content=data,
        media_type=EXCEL_MIME,
        headers={"Content-Disposition": _disposition("人天统计.xlsx")},
    )


@router.get("/reports/status-overview")
def status_overview_report(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """下载多项目状态一览（Excel格式）"""
    try:
        data = generate_status_excel(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败：{str(e)}")

    return Response(
        content=data,
        media_type=EXCEL_MIME,
        headers={"Content-Disposition": _disposition("项目状态一览.xlsx")},
    )


@router.get("/reports/portfolio/word")
def portfolio_report_word(
    report_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """下载项目组合整体报告（Word格式，包含执行摘要/重点关注/全局风险问题/里程碑跟踪/状态一览）"""
    try:
        data = generate_portfolio_report_word(db, report_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败：{str(e)}")

    filename = f"PMO项目组合综合报告_{report_date or date.today()}.docx"
    return Response(
        content=data,
        media_type=WORD_MIME,
        headers={"Content-Disposition": _disposition(filename)},
    )


@router.get("/reports/portfolio/excel")
def portfolio_report_excel(
    report_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """下载项目组合数据汇总（Excel格式，4个Sheet：状态一览/高危问题/高影响风险/逾期里程碑）"""
    try:
        data = generate_portfolio_excel(db, report_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败：{str(e)}")

    filename = f"PMO项目组合数据汇总_{report_date or date.today()}.xlsx"
    return Response(
        content=data,
        media_type=EXCEL_MIME,
        headers={"Content-Disposition": _disposition(filename)},
    )
