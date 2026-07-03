"""
API测试
"""
import os
import sys
from fastapi.testclient import TestClient

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

os.environ.setdefault('TESTING', 'true')
os.environ.setdefault('DATABASE_URL', 'sqlite:///./test.db')

from api.main import app
from models.database import init_db

class TestAPI:
    """API测试类"""

    def setup_method(self):
        init_db()
        self.client = TestClient(app)

    def teardown_method(self):
        self.client.close()
    
    def test_health_check(self):
        """测试健康检查接口"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "timestamp" in data
    
    def test_process_video_invalid_url(self):
        """测试处理无效URL"""
        response = self.client.post(
            "/api/videos/process",
            json={"url": "https://example.com/video/123"}
        )
        
        assert response.status_code == 400
        assert "不支持的视频平台" in response.json()["detail"]
    
    def test_process_video_missing_url(self):
        """测试缺少URL"""
        response = self.client.post(
            "/api/videos/process",
            json={}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_list_videos(self):
        """测试获取视频列表"""
        response = self.client.get("/api/videos")
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "videos" in data
    
    def test_list_videos_with_params(self):
        """测试带参数获取视频列表"""
        response = self.client.get(
            "/api/videos",
            params={
                "page": 1,
                "page_size": 10,
                "status": "completed"
            }
        )
        
        assert response.status_code == 200
    
    def test_get_video_not_found(self):
        """测试获取不存在的视频"""
        response = self.client.get("/api/videos/99999")
        
        assert response.status_code == 404
        assert "视频不存在" in response.json()["detail"]
    
    def test_search_knowledge(self):
        """测试搜索知识库"""
        response = self.client.post(
            "/api/knowledge/search",
            json={"query": "测试", "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "results" in data
    
    def test_search_knowledge_empty_query(self):
        """测试空查询搜索"""
        response = self.client.post(
            "/api/knowledge/search",
            json={"query": "", "limit": 10}
        )
        
        # 应该返回成功但结果为空
        assert response.status_code == 200
    
    def test_get_categories(self):
        """测试获取分类列表"""
        response = self.client.get("/api/knowledge/categories/list")
        
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
    
    def test_get_stats(self):
        """测试获取统计信息"""
        response = self.client.get("/api/knowledge/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_entries" in data
        assert "categories" in data
        assert "category_count" in data
        assert "platform_distribution" in data
    
    def test_export_knowledge(self):
        """测试导出知识库"""
        response = self.client.get("/api/knowledge/export")
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "count" in data
    
    def test_batch_process_empty(self):
        """测试批量处理空列表"""
        response = self.client.post(
            "/api/videos/batch",
            json=[]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_update_video_not_found(self):
        """测试编辑不存在的视频"""
        response = self.client.put(
            "/api/videos/99999",
            json={"title": "新标题"}
        )

        assert response.status_code == 404
        assert "视频不存在" in response.json()["detail"]

    def test_delete_video_not_found(self):
        """测试删除不存在的视频"""
        response = self.client.delete("/api/videos/99999")

        assert response.status_code == 404
        assert "视频不存在" in response.json()["detail"]

    def test_batch_delete_empty_ids(self):
        """测试批量删除空列表"""
        response = self.client.post(
            "/api/videos/delete-batch",
            json={"ids": []}
        )

        assert response.status_code == 400

    def test_category_lifecycle_empty_category(self):
        """测试空分类创建、重命名和删除"""
        create_response = self.client.post(
            "/api/categories",
            json={"name": "测试分类"}
        )
        assert create_response.status_code == 200
        assert create_response.json()["success"] is True

        list_response = self.client.get("/api/categories")
        assert list_response.status_code == 200
        categories = list_response.json()["categories"]
        assert any(category["name"] == "测试分类" for category in categories)

        rename_response = self.client.put(
            "/api/categories/%E6%B5%8B%E8%AF%95%E5%88%86%E7%B1%BB",
            json={"new_name": "升级分类"}
        )
        assert rename_response.status_code == 200
        assert rename_response.json()["success"] is True

        delete_response = self.client.delete("/api/categories/%E5%8D%87%E7%BA%A7%E5%88%86%E7%B1%BB")
        assert delete_response.status_code == 200
        assert delete_response.json()["success"] is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
