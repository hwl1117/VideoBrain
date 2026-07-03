"""
VideoBrain 数据库模型
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./videobrain.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Video(Base):
    """视频记录表"""
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), unique=True, index=True)
    platform = Column(String(50))  # douyin, kuaishou, bilibili, youtube
    title = Column(String(500))
    description = Column(Text)
    duration = Column(Integer)  # 秒
    thumbnail_url = Column(String(500))
    
    # 处理状态
    status = Column(String(20), default="pending")  # pending, downloading, processing, completed, failed
    progress = Column(Integer, default=0)
    error_message = Column(Text)
    
    # 提取内容
    transcript = Column(Text)  # 语音转文字
    key_frames = Column(JSON)  # 关键帧信息
    visual_analysis = Column(JSON)  # 视觉分析结果
    
    # AI概括
    summary = Column(Text)  # 摘要
    key_points = Column(JSON)  # 关键点
    tags = Column(JSON)  # 标签
    category = Column(String(100))  # 分类
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)

class KnowledgeEntry(Base):
    """知识库条目"""
    __tablename__ = "knowledge_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, index=True)
    
    # 知识内容
    title = Column(String(500))
    content = Column(Text)  # 结构化内容
    summary = Column(Text)
    key_insights = Column(JSON)
    
    # 分类和标签
    category = Column(String(100))
    tags = Column(JSON)
    difficulty_level = Column(String(20))  # beginner, intermediate, advanced
    
    # 向量嵌入
    embedding_id = Column(String(100))  # ChromaDB中的ID
    
    # 元数据
    source_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Category(Base):
    """用户自定义分类"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 创建数据库表
def init_db():
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
