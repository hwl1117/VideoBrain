"""
VideoBrain 测试配置
"""
import pytest
import os
import sys
import tempfile

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

@pytest.fixture
def temp_dir():
    """创建临时目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def test_db():
    """创建测试数据库"""
    import tempfile
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from models.database import Base
    
    # 创建临时数据库
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    database_url = f"sqlite:///{db_path}"
    
    engine = create_engine(database_url)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    yield override_get_db
    
    # 清理
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def sample_video_data():
    """示例视频数据"""
    return {
        'url': 'https://www.douyin.com/video/1234567890',
        'platform': 'douyin',
        'title': '测试视频标题',
        'description': '这是一个测试视频的描述',
        'duration': 120,
        'status': 'completed',
        'transcript': '这是视频的语音转文字内容',
        'summary': '这是视频的AI生成摘要',
        'key_points': ['关键点1', '关键点2', '关键点3'],
        'tags': ['测试', 'AI', '视频'],
        'category': '科技'
    }

@pytest.fixture
def sample_knowledge_data():
    """示例知识数据"""
    return {
        'video_id': 1,
        'title': '知识条目标题',
        'content': '# 知识内容\n\n这是详细的知识内容...',
        'summary': '这是知识摘要',
        'metadata': {
            'category': '科技',
            'tags': ['AI', '机器学习'],
            'difficulty_level': 'intermediate',
            'source_url': 'https://example.com',
            'source_platform': 'test',
            'duration': 120
        }
    }

@pytest.fixture(autouse=True)
def setup_test_env():
    """设置测试环境"""
    # 设置环境变量
    os.environ['TESTING'] = 'true'
    os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
    
    yield
    
    # 清理
    if os.path.exists('./test.db'):
        try:
            from models.database import engine
            engine.dispose()
        except Exception:
            pass
        try:
            os.remove('./test.db')
        except PermissionError:
            pass
