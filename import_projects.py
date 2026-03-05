#!/usr/bin/env python3
"""
从 Excel 导出恢复项目数据到 PMO 系统
"""
import requests
import json
from datetime import date

# API 配置
BASE_URL = "http://142.171.178.36:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin123"

# 获取 token
def get_token():
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": USERNAME, "password": PASSWORD}
    )
    if resp.status_code == 200:
        return resp.json()["access_token"]
    else:
        print(f"登录失败: {resp.text}")
        return None

# 阶段映射 - 使用字典 code 值
PHASE_MAP = {
    "立项": "ph_kickoff",
    "计划": "ph_kickoff", 
    "实施": "ph_impl",
    "收尾": "ph_close",
    "验收": "ph_accept"
}

# 状态映射 - 使用字典 code 值
STATUS_MAP = {
    "正常": "st_normal",
    "预警": "st_warn",
    "延期": "st_delay",
    "暂停": "st_pause",
    "关闭": "st_done"
}

# 从 Excel 提取的项目数据
PROJECTS = [
    {"code": "UDNT23H0011-S", "name": "青海电信增值专区跳转需求开发项目", "client": "青海电信", "manager": "薛江涛", "phase": "验收", "status": "暂停"},
    {"code": "UDNT24H0044-SM", "name": "安徽IPTV联通平台技术支撑服务项目", "client": "安徽电信", "manager": None, "phase": "验收", "status": "正常"},
    {"code": "UDNT24H0070-S", "name": "陕西数据运营分析系统建设项目", "client": "陕西电信", "manager": None, "phase": "验收", "status": "延期"},
    {"code": "UDNT25H0007-S", "name": "广东南传2025年IPTV大数据分析系统性能扩容和功能优化项目", "client": "广东电信", "manager": None, "phase": "验收", "status": "延期"},
    {"code": "UDNT25P0007", "name": "福建新质智能多屏应用平台采购项目（电视精灵）", "client": "福建电信", "manager": None, "phase": "验收", "status": "正常"},
    {"code": "UDNT25H0004-S", "name": "陕西AI导视系统建设项目", "client": "陕西电信", "manager": None, "phase": "验收", "status": "延期"},
    {"code": "UDNT25H0005-SP", "name": "新一代福建IPTV集成播控平台建设项目", "client": "福建电信", "manager": None, "phase": "验收", "status": "正常"},
    {"code": "UDNT25H0008-S", "name": "山西IPTV集成播控软件采购项目（五合一）", "client": "山西电信", "manager": None, "phase": "验收", "status": "正常"},
    {"code": "UDNT25H0017-S", "name": "2025年内蒙古IPTV播控平台升级项目服务合同（软件）", "client": "内蒙电信", "manager": None, "phase": "实施", "status": "正常"},
    {"code": "UDNT25H0025", "name": "加快推动IPTV软终端商用(适配电信新版SDK及坚果投影仪）", "client": "深圳电信", "manager": None, "phase": "验收", "status": "延期"},
    {"code": "UDNT25H0037", "name": "四川IPTV智能融合内容管理系统优化项目", "client": "四川电信", "manager": None, "phase": "实施", "status": "正常"},
    {"code": "UDNT24H0001-S", "name": "深圳广信付费单片用户权益优化项目", "client": "深圳电信", "manager": None, "phase": "验收", "status": "延期"},
    {"code": "UDNT24H0032-S", "name": "深圳广信推荐位支持链频道节目预约及回看项目", "client": "深圳电信", "manager": None, "phase": "验收", "status": "延期"},
    {"code": "UDNT25H0023", "name": "2025年北京IPTV运营支撑及安全保障服务项目合同", "client": "北京电信", "manager": None, "phase": "实施", "status": "正常"},
    {"code": "UDNT25H0022", "name": "深圳广信应急广播系统建设项目", "client": "深圳电信", "manager": None, "phase": "验收", "status": "正常"},
    {"code": "UDNT25H0016-M", "name": "内蒙古IPTV播控平台升级项目服务合同", "client": None, "manager": None, "phase": "实施", "status": "正常"},
    {"code": "UDNT25H0027", "name": "北京IPTV（移动侧）平台服务项目合同", "client": None, "manager": None, "phase": "实施", "status": "正常"},
    {"code": "UDNT25H0022-2", "name": "深圳市应急广播 IPTV 系统建设项目采购合同-SWN(非认证软件)", "client": None, "manager": None, "phase": "收尾", "status": "正常"},
    {"code": "UDNT25H0016-S", "name": "2025年内蒙古IPTV播控平台升级项目服务合同（运维）", "client": None, "manager": None, "phase": "实施", "status": "正常"},
    {"code": "UDNT23H0047-M", "name": "浙江IPTV精细运营数据分析系统项目（开发）", "client": "浙江电信", "manager": None, "phase": "验收", "status": "正常"},
    {"code": "UDNT25X0002", "name": "四川金能猫零星开发项目", "client": None, "manager": None, "phase": "实施", "status": "正常"},
    {"code": "UDNT25X0003", "name": "山西传媒集团IPTV集成播控分平台软件五合一项目", "client": None, "manager": None, "phase": "实施", "status": "正常"},
    {"code": "UDNT25X0007", "name": "北京新媒体2025年大数据服务项目", "client": None, "manager": None, "phase": "实施", "status": "正常"},
]

def create_project(project, token):
    """创建单个项目"""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "code": project["code"],
        "name": project["name"],
        "client": project["client"] or "待补充",
        "manager": project["manager"] or "待分配",
        "phase": PHASE_MAP.get(project["phase"], "execution"),
        "status": STATUS_MAP.get(project["status"], "normal"),
        "plan_start": str(date.today()),
        "plan_end": str(date.today()),
        "budget_mandays": 0,
        "description": f"从Excel恢复导入 - 原阶段:{project['phase']}, 原状态:{project['status']}"
    }
    
    try:
        resp = requests.post(
            f"{BASE_URL}/projects/",
            json=payload,
            headers=headers,
            timeout=10
        )
        if resp.status_code == 201:
            print(f"✓ 创建成功: {project['code']}")
            return True
        elif resp.status_code == 400 and "已存在" in resp.text:
            print(f"⚠ 已存在: {project['code']}")
            return False
        else:
            print(f"✗ 失败: {project['code']} - {resp.status_code}: {resp.text[:100]}")
            return False
    except Exception as e:
        print(f"✗ 异常: {project['code']} - {e}")
        return False

def main():
    print(f"开始导入 {len(PROJECTS)} 个项目...")
    print(f"API: {BASE_URL}")
    
    token = get_token()
    if not token:
        print("获取 token 失败，退出")
        return
    print("登录成功，获取 token")
    print()
    
    success = 0
    failed = 0
    skipped = 0
    
    for proj in PROJECTS:
        result = create_project(proj, token)
        if result is True:
            success += 1
        elif result is False:
            skipped += 1
        else:
            failed += 1
    
    print()
    print(f"导入完成: 成功={success}, 跳过={skipped}, 失败={failed}")

if __name__ == "__main__":
    main()
