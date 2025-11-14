"""
管理员 API 路由
提供用户管理和模型管理功能
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import require_admin
from app.models.user import User, UserRole
from app.models.ml_model import ModelStatus, MLModel
from app.models.detection_history import DetectionHistory, DetectionStatus
from app.schemas.user import (
    AdminUserCreate,
    UserResponse,
    UserUpdate,
    UserListResponse,
    BatchUserOperation,
    BatchUpdateStatus,
    PasswordReset,
)
from app.schemas.ml_model import (
    ModelUpload,
    ModelUpdate,
    ModelStatusUpdate,
    ModelResponse,
    ModelListResponse,
)
from app.crud import user as user_crud
from app.crud import ml_model as model_crud
from app.utils.file import save_upload_file, ALLOWED_MODEL_EXTENSIONS, MAX_FILE_SIZE

router = APIRouter()


# Dashboard统计响应模型
class DashboardStats(BaseModel):
    """Dashboard统计数据"""
    user_count: int
    model_count: int
    total_detections: int
    today_detections: int
    detection_trend: List[Dict[str, Any]]  # 最近7天检测趋势
    model_usage: List[Dict[str, Any]]  # 模型使用统计


@router.get("/users", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: str = Query(None, description="搜索关键词（用户名、邮箱）"),
    role: UserRole = Query(None, description="角色筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    获取用户列表（支持分页、搜索、筛选）

    需要管理员权限
    """
    skip = (page - 1) * page_size
    users, total = await user_crud.get_users_with_filter(
        db, skip=skip, limit=page_size, search=search, role=role
    )

    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: AdminUserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    创建用户（管理员可指定角色）

    需要管理员权限
    """
    try:
        # 使用 AdminUserCreate，可以指定角色和激活状态
        from app.schemas.user import UserCreate

        user_create = UserCreate(
            username=user_in.username,
            email=user_in.email,
            password=user_in.password,
        )

        user = await user_crud.create_user(db, user_create, role=user_in.role)

        # 设置激活状态
        if not user_in.is_active:
            user.is_active = user_in.is_active
            await db.commit()
            await db.refresh(user)

        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    获取用户详情

    需要管理员权限
    """
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    更新用户信息

    需要管理员权限
    """
    user = await user_crud.update_user(db, user_id, user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    删除用户

    需要管理员权限
    """
    # 不允许删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己",
        )

    success = await user_crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )


@router.post("/users/{user_id}/reset-password", response_model=dict)
async def reset_user_password(
    user_id: int,
    password_data: PasswordReset,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    重置用户密码（管理员专用）

    需要管理员权限
    管理员可以直接为任何用户设置新密码，无需验证旧密码
    """
    # 验证目标用户是否存在
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    # 更新密码
    await user_crud.update_password(db, user_id, password_data.new_password)

    return {"message": f"已成功重置用户 {user.username} 的密码"}


@router.post("/users/batch/delete")
async def batch_delete_users(
    batch_op: BatchUserOperation,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    批量删除用户

    需要管理员权限
    """
    # 不允许删除自己
    if current_user.id in batch_op.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己",
        )

    count = await user_crud.batch_delete_users(db, batch_op.user_ids)
    return {
        "message": f"成功删除 {count} 个用户",
        "deleted_count": count,
    }


@router.post("/users/batch/update-status")
async def batch_update_status(
    batch_op: BatchUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    批量更新用户状态

    需要管理员权限
    """
    # 不允许修改自己的状态
    if current_user.id in batch_op.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的状态",
        )

    count = await user_crud.batch_update_user_status(
        db, batch_op.user_ids, batch_op.is_active
    )
    status_text = "激活" if batch_op.is_active else "停用"
    return {
        "message": f"成功{status_text} {count} 个用户",
        "updated_count": count,
    }


# ==================== 模型管理 API ====================


@router.post("/models/upload", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def upload_model(
    file: UploadFile = File(..., description="模型文件（.pt或.pth格式）"),
    name: str = Form(..., description="模型名称"),
    version: str = Form(None, description="模型版本"),
    description: str = Form(None, description="模型描述"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    上传机器学习模型文件

    需要管理员权限
    """
    # 保存文件
    try:
        file_path, file_size = await save_upload_file(
            file,
            subdir="models",
            allowed_extensions=ALLOWED_MODEL_EXTENSIONS,
            max_size=MAX_FILE_SIZE,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}",
        )

    # 创建模型记录
    try:
        model = await model_crud.create_model(
            db,
            name=name,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            uploaded_by=current_user.id,
            version=version,
            description=description,
        )
        return ModelResponse.model_validate(model)
    except ValueError as e:
        # 如果数据库创建失败，删除已上传的文件
        from app.utils.file import delete_file
        delete_file(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/models", response_model=ModelListResponse)
async def get_models(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: str = Query(None, description="搜索关键词"),
    model_status: ModelStatus = Query(None, description="状态筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    获取模型列表（支持分页、搜索、筛选）

    需要管理员权限
    """
    skip = (page - 1) * page_size
    models, total = await model_crud.get_models_with_filter(
        db, skip=skip, limit=page_size, search=search, status=model_status
    )

    return ModelListResponse(
        models=[ModelResponse.model_validate(model) for model in models],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/models/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    获取模型详情

    需要管理员权限
    """
    model = await model_crud.get_model_by_id(db, model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型不存在",
        )
    return ModelResponse.model_validate(model)


@router.put("/models/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: int,
    model_in: ModelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    更新模型信息

    需要管理员权限
    """
    model = await model_crud.update_model(
        db,
        model_id,
        name=model_in.name,
        version=model_in.version,
        description=model_in.description,
    )
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型不存在",
        )
    return ModelResponse.model_validate(model)


@router.patch("/models/{model_id}/status", response_model=ModelResponse)
async def update_model_status(
    model_id: int,
    status_update: ModelStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    更新模型状态（激活/停用）

    需要管理员权限
    注意：激活一个模型会自动停用其他所有模型
    """
    model = await model_crud.update_model_status(db, model_id, status_update.status)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型不存在",
        )
    return ModelResponse.model_validate(model)


@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    删除模型及其文件

    需要管理员权限
    """
    success = await model_crud.delete_model(db, model_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型不存在",
        )


@router.get("/stats/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    获取Dashboard统计数据

    返回用户、模型、检测统计以及趋势数据
    需要管理员权限
    """
    # 1. 用户总数
    user_count_result = await db.scalar(select(func.count(User.id)))
    user_count = user_count_result or 0

    # 2. 模型总数
    model_count_result = await db.scalar(select(func.count(MLModel.id)))
    model_count = model_count_result or 0

    # 3. 总检测数
    total_detections_result = await db.scalar(select(func.count(DetectionHistory.id)))
    total_detections = total_detections_result or 0

    # 4. 今日检测数
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_detections_result = await db.scalar(
        select(func.count(DetectionHistory.id)).where(
            DetectionHistory.created_at >= today_start
        )
    )
    today_detections = today_detections_result or 0

    # 5. 最近7天检测趋势
    detection_trend = []
    for i in range(6, -1, -1):
        day_start = (datetime.now() - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        count_result = await db.scalar(
            select(func.count(DetectionHistory.id)).where(
                DetectionHistory.created_at >= day_start,
                DetectionHistory.created_at < day_end
            )
        )
        count = count_result or 0

        detection_trend.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "count": count
        })

    # 6. 模型使用统计（前5个最常用的模型）
    model_usage_query = (
        select(
            MLModel.name,
            func.count(DetectionHistory.id).label("usage_count")
        )
        .join(DetectionHistory, MLModel.id == DetectionHistory.model_id)
        .group_by(MLModel.id, MLModel.name)
        .order_by(func.count(DetectionHistory.id).desc())
        .limit(5)
    )

    model_usage_results = await db.execute(model_usage_query)
    model_usage = [
        {"name": row.name, "count": row.usage_count}
        for row in model_usage_results
    ]

    return DashboardStats(
        user_count=user_count,
        model_count=model_count,
        total_detections=total_detections,
        today_detections=today_detections,
        detection_trend=detection_trend,
        model_usage=model_usage
    )
