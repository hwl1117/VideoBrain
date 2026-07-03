"""
知识库管理服务 - 向量数据库存储和检索
"""
import os
import logging
from typing import Dict, List, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import json
import math

logger = logging.getLogger(__name__)

class KnowledgeBaseManager:
    """知识库管理器，使用ChromaDB进行向量存储和检索"""
    
    def __init__(self, 
                 db_path: str = "./knowledge_base_db",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.embedding_model_name = embedding_model
        self.embedding_model = None
        os.makedirs(db_path, exist_ok=True)
        
        # 初始化ChromaDB
        self.client = chromadb.PersistentClient(path=db_path)
        
        # 创建集合
        self.collection = self.client.get_or_create_collection(
            name="video_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"知识库初始化完成，当前条目数: {self.collection.count()}")

    def _encode_text(self, text: str) -> List[float]:
        """生成嵌入向量；测试环境使用轻量确定性向量避免联网加载模型。"""
        if os.getenv("TESTING") == "true":
            vector = [0.0] * 384
            for char in text.lower():
                vector[ord(char) % len(vector)] += 1.0
            norm = math.sqrt(sum(value * value for value in vector)) or 1.0
            return [value / norm for value in vector]

        if self.embedding_model is None:
            logger.info(f"加载嵌入模型: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
        return self.embedding_model.encode(text).tolist()
    
    def add_knowledge(self, 
                     video_id: int,
                     title: str,
                     content: str,
                     summary: str,
                     metadata: Dict) -> Dict:
        """添加知识条目"""
        try:
            # 生成文档ID
            doc_id = f"video_{video_id}"
            
            # 准备嵌入文本（结合标题、摘要和内容）
            embedding_text = f"{title}\n{summary}\n{content[:1000]}"
            
            # 生成嵌入向量
            embedding = self._encode_text(embedding_text)
            
            # 准备元数据
            chroma_metadata = {
                "video_id": video_id,
                "title": title,
                "summary": summary[:500],
                "category": metadata.get('category', ''),
                "tags": json.dumps(metadata.get('tags', []), ensure_ascii=False),
                "difficulty_level": metadata.get('difficulty_level', 'intermediate'),
                "source_url": metadata.get('source_url', ''),
                "source_platform": metadata.get('source_platform', ''),
                "duration": metadata.get('duration', 0),
                "created_at": metadata.get('created_at', '')
            }
            
            # 存入ChromaDB。使用 upsert 支持重试同一视频时覆盖旧向量。
            self.collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[chroma_metadata]
            )
            
            logger.info(f"知识条目已添加: {doc_id}")
            
            return {
                'success': True,
                'doc_id': doc_id,
                'embedding_size': len(embedding)
            }
            
        except Exception as e:
            logger.error(f"添加知识条目失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search(self, 
               query: str, 
               n_results: int = 10,
               category: Optional[str] = None,
               difficulty: Optional[str] = None,
               platform: Optional[str] = None) -> Dict:
        """搜索知识库"""
        try:
            # 生成查询嵌入
            query_embedding = self._encode_text(query)
            
            # 构建过滤条件
            where_conditions = {}
            if category:
                where_conditions["category"] = category
            if difficulty:
                where_conditions["difficulty_level"] = difficulty
            if platform:
                where_conditions["source_platform"] = platform
            
            # 执行搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_conditions if where_conditions else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # 格式化结果
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'doc_id': results['ids'][0][i],
                    'content': results['documents'][0][i][:500],
                    'metadata': results['metadatas'][0][i],
                    'similarity': 1 - results['distances'][0][i]  # 转换为相似度
                })
            
            return {
                'success': True,
                'results': formatted_results,
                'total': len(formatted_results)
            }
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': []
            }
    
    def get_knowledge(self, video_id: int) -> Optional[Dict]:
        """获取特定知识条目"""
        try:
            doc_id = f"video_{video_id}"
            results = self.collection.get(
                ids=[doc_id],
                include=["documents", "metadatas"]
            )
            
            if results['ids']:
                return {
                    'doc_id': results['ids'][0],
                    'content': results['documents'][0],
                    'metadata': results['metadatas'][0]
                }
            return None
            
        except Exception as e:
            logger.error(f"获取知识条目失败: {e}")
            return None
    
    def update_knowledge(self, video_id: int, updates: Dict) -> Dict:
        """更新知识条目"""
        try:
            doc_id = f"video_{video_id}"
            
            # 获取现有数据
            existing = self.get_knowledge(video_id)
            if not existing:
                return {'success': False, 'error': '条目不存在'}
            
            # 更新元数据
            metadata = existing['metadata']
            metadata.update(updates.get('metadata', {}))
            
            # 更新文档内容
            content = updates.get('content', existing['content'])

            update_kwargs = {
                "ids": [doc_id],
                "documents": [content],
                "metadatas": [metadata],
            }
            if content != existing['content'] or updates.get('metadata', {}).get('title') or updates.get('metadata', {}).get('summary'):
                embedding_text = f"{metadata.get('title', '')}\n{metadata.get('summary', '')}\n{content[:1000]}"
                update_kwargs["embeddings"] = [self._encode_text(embedding_text)]

            # 更新ChromaDB
            self.collection.update(**update_kwargs)
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"更新知识条目失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_knowledge(self, video_id: int) -> Dict:
        """删除知识条目"""
        try:
            doc_id = f"video_{video_id}"
            self.collection.delete(ids=[doc_id])
            return {'success': True}
        except Exception as e:
            logger.error(f"删除知识条目失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_all_categories(self) -> List[str]:
        """获取所有分类"""
        try:
            results = self.collection.get(include=["metadatas"])
            categories = set()
            for metadata in results['metadatas']:
                if metadata.get('category'):
                    categories.add(metadata['category'])
            return sorted(list(categories))
        except Exception as e:
            logger.error(f"获取分类失败: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """获取知识库统计信息"""
        try:
            total = self.collection.count()
            categories = self.get_all_categories()
            
            # 获取平台分布
            results = self.collection.get(include=["metadatas"])
            platform_stats = {}
            for metadata in results['metadatas']:
                platform = metadata.get('source_platform', 'unknown')
                platform_stats[platform] = platform_stats.get(platform, 0) + 1
            
            return {
                'total_entries': total,
                'categories': categories,
                'category_count': len(categories),
                'platform_distribution': platform_stats
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {
                'total_entries': 0,
                'categories': [],
                'category_count': 0,
                'platform_distribution': {}
            }
    
    def export_knowledge(self, format: str = 'json') -> Dict:
        """导出知识库"""
        try:
            results = self.collection.get(include=["documents", "metadatas"])
            
            entries = []
            for i in range(len(results['ids'])):
                entries.append({
                    'id': results['ids'][i],
                    'content': results['documents'][i],
                    'metadata': results['metadatas'][i]
                })
            
            return {
                'success': True,
                'data': entries,
                'format': format,
                'count': len(entries)
            }
        except Exception as e:
            logger.error(f"导出知识库失败: {e}")
            return {'success': False, 'error': str(e)}
