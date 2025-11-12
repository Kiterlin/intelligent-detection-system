"""
文件操作工具函数
"""
import os
import aiofiles
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
from datetime import datetime


# 允许的模型文件扩展名
ALLOWED_MODEL_EXTENSIONS = {".pt", ".pth"}

# 最大文件大小 (500MB)
MAX_FILE_SIZE = 500 * 1024 * 1024


def get_upload_dir(subdir: str = "") -> Path:
    """
    获取上传目录路径

    Args:
        subdir: 子目录名称（如 'models'）

    Returns:
        Path对象
    """
    base_dir = Path(__file__).resolve().parents[2] / "uploads"
    if subdir:
        return base_dir / subdir
    return base_dir


def ensure_upload_dir(subdir: str = "") -> Path:
    """
    确保上传目录存在，不存在则创建

    Args:
        subdir: 子目录名称

    Returns:
        Path对象
    """
    upload_dir = get_upload_dir(subdir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """
    验证文件扩展名

    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名集合

    Returns:
        是否合法
    """
    file_ext = Path(filename).suffix.lower()
    return file_ext in allowed_extensions


def generate_unique_filename(original_filename: str) -> str:
    """
    生成唯一的文件名

    Args:
        original_filename: 原始文件名

    Returns:
        唯一文件名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    file_ext = Path(original_filename).suffix
    file_stem = Path(original_filename).stem
    # 清理文件名，移除特殊字符
    clean_stem = "".join(c for c in file_stem if c.isalnum() or c in ("-", "_"))
    return f"{clean_stem}_{timestamp}{file_ext}"


async def save_upload_file(
    upload_file: UploadFile,
    subdir: str,
    allowed_extensions: set = ALLOWED_MODEL_EXTENSIONS,
    max_size: int = MAX_FILE_SIZE,
) -> tuple[str, int]:
    """
    保存上传的文件

    Args:
        upload_file: FastAPI的UploadFile对象
        subdir: 子目录名称
        allowed_extensions: 允许的文件扩展名集合
        max_size: 最大文件大小（字节）

    Returns:
        (文件路径, 文件大小) 元组

    Raises:
        HTTPException: 文件验证失败或保存失败
    """
    # 验证文件扩展名
    if not validate_file_extension(upload_file.filename, allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式。允许的格式: {', '.join(allowed_extensions)}",
        )

    # 确保上传目录存在
    upload_dir = ensure_upload_dir(subdir)

    # 生成唯一文件名
    unique_filename = generate_unique_filename(upload_file.filename)
    file_path = upload_dir / unique_filename

    # 保存文件并计算大小
    file_size = 0
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await upload_file.read(8192):  # 8KB chunks
                file_size += len(chunk)

                # 检查文件大小
                if file_size > max_size:
                    # 删除已写入的部分文件
                    await f.close()
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=413,
                        detail=f"文件大小超过限制 ({max_size / (1024 * 1024):.0f}MB)",
                    )

                await f.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        # 如果保存失败，删除部分文件
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"文件保存失败: {str(e)}",
        )

    # 返回相对路径和文件大小
    relative_path = str(file_path.relative_to(Path(__file__).resolve().parents[2]))
    return relative_path, file_size


def delete_file(file_path: str) -> bool:
    """
    删除文件

    Args:
        file_path: 文件路径（相对于项目根目录）

    Returns:
        是否删除成功
    """
    try:
        base_dir = Path(__file__).resolve().parents[2]
        full_path = base_dir / file_path

        if full_path.exists() and full_path.is_file():
            os.remove(full_path)
            return True
        return False
    except Exception:
        return False


def get_file_size(file_path: str) -> Optional[int]:
    """
    获取文件大小

    Args:
        file_path: 文件路径（相对于项目根目录）

    Returns:
        文件大小（字节），文件不存在则返回None
    """
    try:
        base_dir = Path(__file__).resolve().parents[2]
        full_path = base_dir / file_path

        if full_path.exists() and full_path.is_file():
            return full_path.stat().st_size
        return None
    except Exception:
        return None
