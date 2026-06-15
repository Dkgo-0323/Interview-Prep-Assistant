# api/routes/profile.py
# Day 2 上午完整实现，今天先确保服务能启动
import logging
from fastapi import APIRouter, HTTPException
from api.main import get_session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", summary="生成求职画像（Day 2 实现）")
async def generate_profile():
    """求职画像生成 - Day 2 上午实现"""
    session = get_session()
    if "resume_text" not in session:
        raise HTTPException(status_code=400, detail="请先上传简历")

    # Day 2 实现真实逻辑，今天返回占位数据
    return {
        "success": True,
        "profile": {
            "core_strengths": ["待 Day 2 实现"],
            "suitable_company_size": "待实现",
            "career_stage": "待实现",
            "search_keywords": ["待实现"],
            "positioning_summary": "求职画像功能将在 Day 2 上午完成",
            "salary_range_estimate": "待实现",
        },
    }