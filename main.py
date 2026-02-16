#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
任务管理API - 部署版本
适合部署到 Render / Replit 等免费服务器
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uvicorn
import os
import sys
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 尝试导入远程存储，如果失败则使用模拟数据
try:
    from data.remote_storage import RemoteStorage
    from data.access import Task, SyncStatus
    HAS_REMOTE_STORAGE = True
except Exception as e:
    print(f"警告: 无法导入远程存储模块，将使用模拟数据: {e}")
    HAS_REMOTE_STORAGE = False


app = FastAPI(
    title="任务管理API",
    description="为安卓App提供任务查询接口 - 部署版本",
    version="1.0.0"
)

# 配置CORS（允许跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic模型定义
class TaskResponse(BaseModel):
    id: str
    title: str
    detail: Optional[str]
    status: str
    task_date: Optional[str]
    assignee: Optional[str]
    shift_type: Optional[str]
    created_at: str
    updated_at: str


class TaskListResponse(BaseModel):
    success: bool
    message: str
    data: List[TaskResponse]
    total: int


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    message: str
    token: Optional[str] = None
    user_id: Optional[str] = None


# 模拟数据（当无法连接数据库时使用）
MOCK_TASKS = [
    {
        "id": "task-001",
        "title": "完成项目文档",
        "detail": "编写完整的项目开发文档",
        "status": "todo",
        "task_date": "2026-02-16",
        "assignee": "张三",
        "shift_type": "白班",
        "created_at": "2026-02-15 09:00:00",
        "updated_at": "2026-02-15 09:00:00"
    },
    {
        "id": "task-002",
        "title": "代码审查",
        "detail": "审查最新提交的代码",
        "status": "done",
        "task_date": "2026-02-15",
        "assignee": "李四",
        "shift_type": "夜班",
        "created_at": "2026-02-14 14:00:00",
        "updated_at": "2026-02-15 10:00:00"
    },
    {
        "id": "task-003",
        "title": "测试新功能",
        "detail": "测试新开发的功能模块",
        "status": "todo",
        "task_date": "2026-02-16",
        "assignee": "王五",
        "shift_type": "白班",
        "created_at": "2026-02-15 11:00:00",
        "updated_at": "2026-02-15 11:00:00"
    }
]

# 模拟用户数据库
MOCK_USERS = {
    "admin": {
        "password": "123456",
        "user_id": "user-001"
    },
    "test": {
        "password": "test123",
        "user_id": "user-002"
    }
}


# 全局存储实例
remote_storage: Optional[RemoteStorage] = None


def get_remote_storage():
    """获取远程存储实例"""
    global remote_storage
    if not HAS_REMOTE_STORAGE:
        return None
    
    if remote_storage is None:
        try:
            remote_storage = RemoteStorage()
        except Exception as e:
            print(f"初始化远程存储失败: {e}")
            return None
    
    if not remote_storage.is_connected():
        try:
            if not remote_storage.connect():
                return None
        except Exception as e:
            print(f"连接远程数据库失败: {e}")
            return None
    
    return remote_storage


def mock_task_to_response(task_data: Dict) -> TaskResponse:
    """将模拟数据转换为响应格式"""
    return TaskResponse(**task_data)


def task_to_response(task: Task) -> TaskResponse:
    """将Task对象转换为API响应格式"""
    return TaskResponse(
        id=task.id,
        title=task.title,
        detail=task.detail,
        status=task.status,
        task_date=task.task_date,
        assignee=task.assignee,
        shift_type=task.shift_type,
        created_at=task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        updated_at=task.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    )


@app.get("/")
async def root():
    """根路径，返回服务信息"""
    return {
        "service": "任务管理API",
        "version": "1.0.0",
        "status": "running",
        "mode": "database" if HAS_REMOTE_STORAGE and get_remote_storage() else "mock",
        "endpoints": {
            "服务信息": "/",
            "登录": "/login",
            "任务列表": "/api/tasks/{user_id}",
            "今日任务": "/api/tasks/{user_id}/today",
            "待办任务": "/api/tasks/{user_id}/todo",
            "已完成任务": "/api/tasks/{user_id}/done",
            "按日期查询": "/api/tasks/{user_id}/date/{task_date}",
            "API文档": "/docs"
        }
    }


@app.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """模拟登录接口"""
    user = MOCK_USERS.get(request.username)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    token = f"token-{request.username}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return LoginResponse(
        message="登录成功",
        token=token,
        user_id=user["user_id"]
    )


@app.get("/get-time")
async def get_time():
    """获取服务器时间 - 简单测试接口"""
    timestamp = datetime.now().isoformat()
    return {
        "timestamp": timestamp,
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@app.get("/api/tasks/{user_id}", response_model=TaskListResponse)
async def get_tasks(
    user_id: str,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    获取任务列表
    
    参数:
        user_id: 用户ID
        status: 任务状态 (todo/done)，可选
        start_date: 开始日期 (YYYY-MM-DD)，可选
        end_date: 结束日期 (YYYY-MM-DD)，可选
    """
    storage = get_remote_storage()
    
    if storage:
        try:
            # 使用真实数据库
            all_tasks = storage.get_tasks(user_id, status=status)
            active_tasks = [task for task in all_tasks if not task.is_deleted]
            
            # 按日期范围过滤
            if start_date or end_date:
                filtered_tasks = []
                for task in active_tasks:
                    if not task.task_date:
                        continue
                    task_date = task.task_date
                    if start_date and task_date < start_date:
                        continue
                    if end_date and task_date > end_date:
                        continue
                    filtered_tasks.append(task)
                active_tasks = filtered_tasks
            
            # 按更新时间倒序排序
            active_tasks.sort(key=lambda x: x.updated_at, reverse=True)
            
            response_tasks = [task_to_response(task) for task in active_tasks]
            
            return TaskListResponse(
                success=True,
                message="获取成功",
                data=response_tasks,
                total=len(response_tasks)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取任务失败: {str(e)}")
    else:
        # 使用模拟数据
        tasks = MOCK_TASKS.copy()
        
        # 按状态过滤
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        
        # 按日期范围过滤
        if start_date or end_date:
            filtered = []
            for t in tasks:
                task_date = t["task_date"]
                if not task_date:
                    continue
                if start_date and task_date < start_date:
                    continue
                if end_date and task_date > end_date:
                    continue
                filtered.append(t)
            tasks = filtered
        
        response_tasks = [mock_task_to_response(t) for t in tasks]
        
        return TaskListResponse(
            success=True,
            message="获取成功 (模拟数据)",
            data=response_tasks,
            total=len(response_tasks)
        )


@app.get("/api/tasks/{user_id}/today", response_model=TaskListResponse)
async def get_today_tasks(user_id: str):
    """获取今日任务"""
    today = date.today().strftime("%Y-%m-%d")
    return await get_tasks(user_id, start_date=today, end_date=today)


@app.get("/api/tasks/{user_id}/todo", response_model=TaskListResponse)
async def get_todo_tasks(user_id: str):
    """获取待办任务"""
    return await get_tasks(user_id, status="todo")


@app.get("/api/tasks/{user_id}/done", response_model=TaskListResponse)
async def get_done_tasks(user_id: str):
    """获取已完成任务"""
    return await get_tasks(user_id, status="done")


@app.get("/api/tasks/{user_id}/date/{task_date}", response_model=TaskListResponse)
async def get_tasks_by_date(user_id: str, task_date: str):
    """按指定日期查询任务 (格式: YYYY-MM-DD)"""
    return await get_tasks(user_id, start_date=task_date, end_date=task_date)


@app.get("/health")
async def health_check():
    """健康检查接口"""
    storage = get_remote_storage()
    return {
        "status": "healthy",
        "database": "connected" if storage else "mock_mode",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("=" * 60)
    print("任务管理API服务启动中...")
    print("=" * 60)
    print(f"服务地址: http://0.0.0.0:{port}")
    print(f"API文档: http://0.0.0.0:{port}/docs")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False
    )
