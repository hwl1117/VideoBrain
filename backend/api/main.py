"""
VideoBrain 主API服务
"""
import os
import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from models.database import Category, init_db, get_db, Video, KnowledgeEntry
from middleware.error_handler import ErrorHandlerMiddleware
from middleware.request_logger import RequestLoggerMiddleware
from services.video_downloader import VideoDownloader
from services.audio_extractor import AudioExtractor
from services.speech_to_text import SpeechToTextService
from services.visual_analyzer import VisualAnalyzer
from services.ai_summarizer import AISummarizer
from services.knowledge_base import KnowledgeBaseManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化FastAPI应用
app = FastAPI(
    title="VideoBrain API",
    description="短视频智能知识库系统",
    version="1.0.0"
)

# CORS配置 — 限制为实际前端域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 接入自定义中间件
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggerMiddleware)

# 服务按需初始化，避免健康检查、测试和普通查询被 AI key 或模型冷启动阻塞。
video_downloader: Optional[VideoDownloader] = None
audio_extractor: Optional[AudioExtractor] = None
speech_to_text: Optional[SpeechToTextService] = None
visual_analyzer: Optional[VisualAnalyzer] = None
ai_summarizer: Optional[AISummarizer] = None
knowledge_base: Optional[KnowledgeBaseManager] = None

def get_video_downloader() -> VideoDownloader:
    global video_downloader
    if video_downloader is None:
        video_downloader = VideoDownloader()
    return video_downloader

def get_audio_extractor() -> AudioExtractor:
    global audio_extractor
    if audio_extractor is None:
        audio_extractor = AudioExtractor()
    return audio_extractor

def get_speech_to_text() -> SpeechToTextService:
    global speech_to_text
    if speech_to_text is None:
        speech_to_text = SpeechToTextService()
    return speech_to_text

def get_visual_analyzer() -> VisualAnalyzer:
    global visual_analyzer
    if visual_analyzer is None:
        visual_analyzer = VisualAnalyzer()
    return visual_analyzer

def get_ai_summarizer() -> AISummarizer:
    global ai_summarizer
    if ai_summarizer is None:
        ai_summarizer = AISummarizer()
    return ai_summarizer

def get_knowledge_base() -> KnowledgeBaseManager:
    global knowledge_base
    if knowledge_base is None:
        knowledge_base = KnowledgeBaseManager()
    return knowledge_base

# 数据模型
class VideoURLRequest(BaseModel):
    url: str
    language: Optional[str] = "zh"

class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    difficulty: Optional[str] = None
    platform: Optional[str] = None
    limit: Optional[int] = 10

class VideoUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None

class BatchDeleteRequest(BaseModel):
    ids: List[int]

class CategoryRequest(BaseModel):
    name: str
    video_ids: Optional[List[int]] = None

class CategoryRenameRequest(BaseModel):
    new_name: str

class CategoryMoveRequest(BaseModel):
    video_ids: List[int]
    target_category: Optional[str] = ""

class ProcessingStatus(BaseModel):
    video_id: int
    status: str
    progress: int
    message: str

def video_to_dict(video: Video, include_detail: bool = True) -> Dict[str, Any]:
    transcript = video.transcript or ""
    payload: Dict[str, Any] = {
        "id": video.id,
        "url": video.url,
        "platform": video.platform,
        "title": video.title,
        "description": video.description,
        "duration": video.duration,
        "thumbnail_url": video.thumbnail_url,
        "status": video.status,
        "progress": video.progress,
        "error_message": video.error_message,
        "summary": video.summary,
        "one_line_summary": (video.summary or "")[:120],
        "key_points": video.key_points or [],
        "tags": video.tags or [],
        "category": video.category or "",
        "created_at": video.created_at,
        "updated_at": video.updated_at,
        "processed_at": video.processed_at,
        "transcript_preview": transcript[:200] + ("..." if len(transcript) > 200 else ""),
        "transcript_length": len(transcript),
        "has_transcript": len(transcript) > 10,
    }
    if include_detail:
        payload["transcript"] = transcript
        payload["key_frames"] = video.key_frames or []
        payload["visual_analysis"] = video.visual_analysis
    return payload

def ensure_category(db: Session, name: Optional[str]) -> None:
    clean_name = (name or "").strip()
    if not clean_name:
        return
    exists = db.query(Category).filter(Category.name == clean_name).first()
    if not exists:
        db.add(Category(name=clean_name))

def update_knowledge_metadata(video_id: int, metadata: Dict[str, Any], content: Optional[str] = None) -> None:
    updates: Dict[str, Any] = {"metadata": metadata}
    if content is not None:
        updates["content"] = content
    try:
        get_knowledge_base().update_knowledge(video_id, updates)
    except Exception as exc:
        logger.warning(f"同步向量知识库失败 video_id={video_id}: {exc}")

def build_category_response(db: Session) -> Dict[str, Any]:
    categories: Dict[str, Dict[str, Any]] = {}
    for category in db.query(Category).order_by(Category.name.asc()).all():
        categories[category.name] = {"name": category.name, "count": 0, "videos": []}

    uncategorized = {"name": "未分类", "count": 0, "videos": []}
    for video in db.query(Video).order_by(Video.created_at.desc()).all():
        item = {
            "id": video.id,
            "title": video.title,
            "platform": video.platform,
            "one_line_summary": (video.summary or "")[:120],
        }
        category_name = (video.category or "").strip()
        if category_name:
            categories.setdefault(category_name, {"name": category_name, "count": 0, "videos": []})
            categories[category_name]["count"] += 1
            categories[category_name]["videos"].append(item)
        else:
            uncategorized["count"] += 1
            uncategorized["videos"].append(item)

    category_list = sorted(categories.values(), key=lambda item: (-item["count"], item["name"]))
    return {
        "categories": category_list,
        "uncategorized": uncategorized,
        "total_categories": len(category_list),
        "total_videos": db.query(Video).count(),
    }

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()
    logger.info("VideoBrain API 启动完成")

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "VideoBrain API",
        "timestamp": datetime.utcnow().isoformat()
    }

# 重试处理
@app.post("/api/videos/{video_id}/retry")
async def retry_video(video_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """重试失败的视频处理"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    if video.status not in ["failed", "completed", "processing"]:
        raise HTTPException(status_code=400, detail="只能重试失败、已完成或卡住的视频")

    # 重置状态
    video.status = "pending"
    video.progress = 0
    video.error_message = None
    db.commit()

    # 重新提交后台任务
    background_tasks.add_task(
        process_video_pipeline,
        video.id,
        video.url,
        "zh",
        video.platform
    )

    return {"video_id": video.id, "status": "pending", "message": "重试任务已创建"}

# 视频处理接口
@app.post("/api/videos/process")
async def process_video(request: VideoURLRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """处理视频链接"""
    try:
        downloader = get_video_downloader()
        # 验证URL
        platform = downloader.detect_platform(request.url)
        if not platform:
            raise HTTPException(status_code=400, detail="不支持的视频平台")
        
        # 检查是否已处理过
        existing_video = db.query(Video).filter(Video.url == request.url).first()
        if existing_video:
            if existing_video.status == "completed":
                return {
                    "video_id": existing_video.id,
                    "status": "completed",
                    "message": "视频已处理完成"
                }
            elif existing_video.status in ["pending", "downloading", "processing"]:
                return {
                    "video_id": existing_video.id,
                    "status": existing_video.status,
                    "message": "视频正在处理中"
                }
        
        # 获取视频信息（同步阻塞调用放到线程池）
        video_info = await asyncio.to_thread(downloader.get_video_info, request.url)
        
        # 创建视频记录
        video = Video(
            url=request.url,
            platform=platform,
            title=video_info.get('title', ''),
            description=video_info.get('description', ''),
            duration=video_info.get('duration', 0),
            thumbnail_url=video_info.get('thumbnail', ''),
            status="pending",
            progress=0
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        
        # 后台处理任务
        background_tasks.add_task(
            process_video_pipeline,
            video.id,
            request.url,
            request.language,
            platform
        )
        
        return {
            "video_id": video.id,
            "status": "pending",
            "message": "视频处理任务已创建"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理视频失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_video_pipeline(video_id: int, url: str, language: str, platform: str):
    """视频处理流水线"""
    from models.database import SessionLocal
    
    db = SessionLocal()
    try:
        downloader = get_video_downloader()
        extractor = get_audio_extractor()
        transcriber = get_speech_to_text()
        vision = get_visual_analyzer()
        summarizer = get_ai_summarizer()
        kb = get_knowledge_base()

        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return
        
        # 更新状态为下载中
        video.status = "downloading"
        video.progress = 10
        db.commit()
        
        # 1. 下载视频
        logger.info(f"开始下载视频: {url}")
        download_result = downloader.download_video(url)
        
        if not download_result['success']:
            video.status = "failed"
            video.error_message = f"下载失败: {download_result.get('error', '未知错误')}"
            db.commit()
            return
        
        video_path = download_result['file_path']
        video.progress = 30
        db.commit()
        
        # 2. 提取音频
        logger.info("开始提取音频")
        video.status = "processing"
        audio_result = extractor.extract_audio(video_path)
        
        if not audio_result['success']:
            video.status = "failed"
            video.error_message = f"音频提取失败: {audio_result.get('error', '未知错误')}"
            db.commit()
            downloader.cleanup(video_path)
            return
        
        audio_path = audio_result['output_path']
        video.progress = 50
        db.commit()
        
        # 3. 语音转文字
        logger.info("开始语音转文字")
        transcript_result = transcriber.transcribe_audio(audio_path, language)

        if not transcript_result['success']:
            video.status = "failed"
            video.error_message = f"语音转文字失败: {transcript_result.get('error', '未知错误')}"
            db.commit()
            extractor.cleanup(audio_path)
            downloader.cleanup(video_path)
            return

        video.transcript = transcript_result['text']
        video.progress = 70
        db.commit()
        
        # 4. 视觉分析
        logger.info("开始视觉分析")
        frames = extractor.extract_key_frames(video_path)
        
        if frames:
            frame_paths = [f['path'] for f in frames]
            visual_result = vision.analyze_video_frames(frame_paths, video.title)
            
            if visual_result['success']:
                video.key_frames = [{'path': f['path'], 'index': f['index']} for f in frames]
                video.visual_analysis = visual_result['combined_analysis']
        
        video.progress = 85
        db.commit()
        
        # 5. AI概括
        logger.info("开始AI概括")
        if video.transcript:
            summary_result = summarizer.generate_knowledge_entry(
                video_data={
                    'title': video.title,
                    'description': video.description,
                    'url': url,
                    'platform': platform,
                    'duration': video.duration
                },
                transcript=video.transcript,
                visual_analysis=video.visual_analysis or ''
            )
            
            if summary_result['success']:
                entry_data = summary_result['knowledge_entry']
                
                video.summary = entry_data.get('summary', '')
                video.key_points = entry_data.get('key_points', [])
                video.tags = entry_data.get('tags', [])
                video.category = entry_data.get('category', '')
                
                # 6. 存入知识库
                logger.info("存入知识库")
                kb_result = kb.add_knowledge(
                    video_id=video_id,
                    title=video.title,
                    content=entry_data.get('content', ''),
                    summary=entry_data.get('summary', ''),
                    metadata={
                        'category': entry_data.get('category', ''),
                        'tags': entry_data.get('tags', []),
                        'difficulty_level': entry_data.get('difficulty_level', 'intermediate'),
                        'source_url': url,
                        'source_platform': platform,
                        'duration': video.duration,
                        'created_at': datetime.utcnow().isoformat()
                    }
                )
                
                if kb_result['success']:
                    # 创建知识库条目记录
                    knowledge_entry = KnowledgeEntry(
                        video_id=video_id,
                        title=video.title,
                        content=entry_data.get('content', ''),
                        summary=entry_data.get('summary', ''),
                        key_insights=entry_data.get('key_insights', []),
                        category=entry_data.get('category', ''),
                        tags=entry_data.get('tags', []),
                        difficulty_level=entry_data.get('difficulty_level', 'intermediate'),
                        embedding_id=kb_result['doc_id'],
                        source_url=url
                    )
                    db.add(knowledge_entry)
        
        # 更新完成状态
        video.status = "completed"
        video.progress = 100
        video.processed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"视频处理完成: {video_id}")
        
        # 清理临时文件
        extractor.cleanup(audio_path)
        downloader.cleanup(video_path)
        
    except Exception as e:
        logger.error(f"处理流水线失败: {e}")
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status = "failed"
            video.error_message = str(e)
            db.commit()
    finally:
        db.close()

# 查询接口
@app.get("/api/videos/{video_id}")
async def get_video(video_id: int, db: Session = Depends(get_db)):
    """获取视频信息"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    return video_to_dict(video)

@app.put("/api/videos/{video_id}")
async def update_video(video_id: int, request: VideoUpdateRequest, db: Session = Depends(get_db)):
    """编辑视频知识条目"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    updates = request.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(video, field, value)

    if "category" in updates:
        ensure_category(db, updates["category"])

    entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.video_id == video_id).first()
    if entry:
        if "title" in updates:
            entry.title = video.title
        if "summary" in updates:
            entry.summary = video.summary
        if "key_points" in updates:
            entry.key_insights = video.key_points
        if "tags" in updates:
            entry.tags = video.tags
        if "category" in updates:
            entry.category = video.category
        if "transcript" in updates or "summary" in updates or "key_points" in updates:
            entry.content = f"{video.transcript or ''}\n\n摘要：{video.summary or ''}\n\n关键点：\n" + "\n".join(video.key_points or [])

    db.commit()
    db.refresh(video)

    update_knowledge_metadata(
        video_id,
        {
            "title": video.title or "",
            "summary": video.summary or "",
            "category": video.category or "",
            "tags": video.tags or [],
            "source_platform": video.platform or "",
            "source_url": video.url or "",
        },
        entry.content if entry else None,
    )

    return {"success": True, "video": video_to_dict(video)}

@app.delete("/api/videos/{video_id}")
async def delete_video(video_id: int, db: Session = Depends(get_db)):
    """删除视频和对应知识条目"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    title = video.title
    db.query(KnowledgeEntry).filter(KnowledgeEntry.video_id == video_id).delete()
    db.delete(video)
    db.commit()

    try:
        get_knowledge_base().delete_knowledge(video_id)
    except Exception as exc:
        logger.warning(f"删除向量知识条目失败 video_id={video_id}: {exc}")

    return {"success": True, "message": f"视频「{title or video_id}」已删除", "deleted_id": video_id}

@app.get("/api/videos")
async def list_videos(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取视频列表"""
    query = db.query(Video)
    
    if status:
        query = query.filter(Video.status == status)
    if platform:
        query = query.filter(Video.platform == platform)
    
    total = query.count()
    videos = query.order_by(Video.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "videos": [video_to_dict(v, include_detail=False) for v in videos]
    }

# 知识库搜索接口
@app.post("/api/knowledge/search")
async def search_knowledge(request: SearchRequest):
    """搜索知识库"""
    result = get_knowledge_base().search(
        query=request.query,
        n_results=request.limit,
        category=request.category,
        difficulty=request.difficulty,
        platform=request.platform
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', '搜索失败'))
    
    return result

@app.get("/api/knowledge/categories/list")
async def list_categories():
    """获取所有分类"""
    categories = get_knowledge_base().get_all_categories()
    return {"categories": categories}

@app.get("/api/knowledge/stats")
async def get_statistics():
    """获取知识库统计"""
    return get_knowledge_base().get_statistics()

# 批量处理接口
@app.post("/api/videos/batch")
async def batch_process_videos(urls: List[str], background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """批量处理视频"""
    results = []
    downloader = get_video_downloader()
    
    for url in urls:
        try:
            platform = downloader.detect_platform(url)
            if not platform:
                results.append({"url": url, "status": "error", "message": "不支持的平台"})
                continue
            
            # 检查是否已存在
            existing = db.query(Video).filter(Video.url == url).first()
            if existing:
                results.append({"url": url, "video_id": existing.id, "status": existing.status})
                continue
            
            # 创建记录
            video = Video(url=url, platform=platform, status="pending")
            db.add(video)
            db.commit()
            db.refresh(video)
            
            # 添加后台任务
            background_tasks.add_task(process_video_pipeline, video.id, url, "zh", platform)
            
            results.append({"url": url, "video_id": video.id, "status": "pending"})
            
        except Exception as e:
            results.append({"url": url, "status": "error", "message": str(e)})
    
    return {"results": results, "total": len(urls)}

@app.post("/api/videos/delete-batch")
async def batch_delete_videos(request: BatchDeleteRequest, db: Session = Depends(get_db)):
    """批量删除视频和知识条目"""
    if not request.ids:
        raise HTTPException(status_code=400, detail="请提供要删除的视频ID")

    deleted = []
    not_found = []
    for video_id in request.ids:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            not_found.append(video_id)
            continue

        deleted.append({"id": video_id, "title": video.title})
        db.query(KnowledgeEntry).filter(KnowledgeEntry.video_id == video_id).delete()
        db.delete(video)

        try:
            get_knowledge_base().delete_knowledge(video_id)
        except Exception as exc:
            logger.warning(f"批量删除向量知识条目失败 video_id={video_id}: {exc}")

    db.commit()
    return {
        "success": True,
        "deleted": deleted,
        "not_found": not_found,
        "deleted_count": len(deleted),
    }

@app.get("/api/categories")
async def get_categories(db: Session = Depends(get_db)):
    """获取分类及分类下视频"""
    return build_category_response(db)

@app.post("/api/categories")
async def create_category(request: CategoryRequest, db: Session = Depends(get_db)):
    """创建分类，可选地把视频移入该分类"""
    name = request.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="分类名称不能为空")

    ensure_category(db, name)
    updated_ids = []
    for video_id in request.video_ids or []:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            continue
        video.category = name
        updated_ids.append(video_id)

        entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.video_id == video_id).first()
        if entry:
            entry.category = name
        update_knowledge_metadata(video_id, {"category": name})

    db.commit()
    return {"success": True, "category": name, "updated_count": len(updated_ids), "updated_ids": updated_ids}

@app.put("/api/categories/{name}")
async def rename_category(name: str, request: CategoryRenameRequest, db: Session = Depends(get_db)):
    """重命名分类"""
    old_name = name.strip()
    new_name = request.new_name.strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="新分类名称不能为空")

    category = db.query(Category).filter(Category.name == old_name).first()
    if category:
        category.name = new_name
    else:
        ensure_category(db, new_name)

    updated_count = 0
    for video in db.query(Video).filter(Video.category == old_name).all():
        video.category = new_name
        updated_count += 1
        update_knowledge_metadata(video.id, {"category": new_name})

    for entry in db.query(KnowledgeEntry).filter(KnowledgeEntry.category == old_name).all():
        entry.category = new_name

    db.commit()
    return {"success": True, "old_name": old_name, "new_name": new_name, "updated_count": updated_count}

@app.delete("/api/categories/{name}")
async def delete_category(name: str, db: Session = Depends(get_db)):
    """删除分类，并把该分类下视频移入未分类"""
    category_name = name.strip()
    moved_count = 0
    for video in db.query(Video).filter(Video.category == category_name).all():
        video.category = ""
        moved_count += 1
        update_knowledge_metadata(video.id, {"category": ""})

    for entry in db.query(KnowledgeEntry).filter(KnowledgeEntry.category == category_name).all():
        entry.category = ""

    category = db.query(Category).filter(Category.name == category_name).first()
    if category:
        db.delete(category)

    db.commit()
    return {"success": True, "deleted_category": category_name, "moved_to_uncategorized": moved_count}

@app.post("/api/categories/move")
async def move_videos_to_category(request: CategoryMoveRequest, db: Session = Depends(get_db)):
    """批量移动视频到分类"""
    if not request.video_ids:
        raise HTTPException(status_code=400, detail="请提供视频ID数组")

    target = (request.target_category or "").strip()
    ensure_category(db, target)
    moved = []

    for video_id in request.video_ids:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            continue
        video.category = target
        moved.append(video_id)

        entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.video_id == video_id).first()
        if entry:
            entry.category = target
        update_knowledge_metadata(video_id, {"category": target})

    db.commit()
    return {"success": True, "target_category": target or "未分类", "moved_count": len(moved), "moved_ids": moved}

# 导出接口
@app.get("/api/knowledge/export")
async def export_knowledge(format: str = "json"):
    """导出知识库"""
    result = get_knowledge_base().export_knowledge(format)
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', '导出失败'))
    return result

@app.get("/api/knowledge/{video_id}")
async def get_knowledge_entry(video_id: int):
    """获取知识库条目"""
    entry = get_knowledge_base().get_knowledge(video_id)
    if not entry:
        raise HTTPException(status_code=404, detail="知识条目不存在")
    return entry

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
