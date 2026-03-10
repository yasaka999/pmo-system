"""
操作日志记录
用于记录用户的关键操作行为
"""
from fastapi import Request
from app.models.operation_log import OperationLog
from app.db.session import SessionLocal
from app.models.user import User
import threading

def record_operation(
    action: str,
    module: str,
    description: str,
    request: Request,
    current_user: User
):
    """
    异步记录操作日志
    
    Args:
        action: 操作类型 (CREATE/UPDATE/DELETE/LOGIN/LOGOUT)
        module: 模块名称
        description: 操作描述
        request: FastAPI Request 对象
        current_user: 当前用户对象
    """
    def save_log():
        try:
            db = SessionLocal()
            log_entry = OperationLog(
                user_id=current_user.id,
                username=current_user.username,
                action=action,
                module=module,
                description=description,
                request_method=request.method,
                request_url=str(request.url),
                ip_address=request.client.host if request.client else "",
                user_agent=request.headers.get("user-agent", "")
            )
            db.add(log_entry)
            db.commit()
            db.close()
            print(f"[LOG] {action} - {module}: {description}")
        except Exception as e:
            print(f"Operation log save error: {e}")
    
    # 使用线程异步写入（不阻塞主流程）
    thread = threading.Thread(target=save_log)
    thread.start()
