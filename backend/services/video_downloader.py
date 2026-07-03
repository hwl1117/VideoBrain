"""
视频下载服务 - 支持多平台短视频下载
"""
import os
import re
import hashlib
import yt_dlp
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class VideoDownloader:
    """视频下载器，支持抖音、快手、B站、YouTube等平台"""
    
    # 平台配置
    PLATFORM_CONFIGS = {
        'douyin': {
            'name': '抖音',
            'url_patterns': ['douyin.com', 'iesdouyin.com'],
            'extractor': 'douyin'
        },
        'kuaishou': {
            'name': '快手',
            'url_patterns': ['kuaishou.com', 'gifshow.com'],
            'extractor': 'kuaishou'
        },
        'bilibili': {
            'name': 'B站',
            'url_patterns': ['bilibili.com', 'b23.tv'],
            'extractor': 'bilibili'
        },
        'youtube': {
            'name': 'YouTube',
            'url_patterns': ['youtube.com', 'youtu.be'],
            'extractor': 'youtube'
        },
        'tiktok': {
            'name': 'TikTok',
            'url_patterns': ['tiktok.com'],
            'extractor': 'tiktok'
        },
        'xiaohongshu': {
            'name': '小红书',
            'url_patterns': ['xiaohongshu.com', 'xhslink.com'],
            'extractor': 'xiaohongshu'
        }
    }
    
    def __init__(self, output_dir: str = "./downloads"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def detect_platform(self, url: str) -> Optional[str]:
        """检测视频平台"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        for platform, config in self.PLATFORM_CONFIGS.items():
            for pattern in config['url_patterns']:
                if pattern in domain:
                    return platform
        return None
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """获取视频信息（不下载）"""
        platform = self.detect_platform(url)
        if not platform:
            raise ValueError(f"不支持的视频平台: {url}")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', ''),
                    'description': info.get('description', ''),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'platform': platform,
                    'url': url,
                    'uploader': info.get('uploader', ''),
                    'upload_date': info.get('upload_date', ''),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                }
        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            raise
    
    def download_video(self, url: str, progress_callback=None) -> Dict[str, Any]:
        """下载视频"""
        platform = self.detect_platform(url)
        if not platform:
            raise ValueError(f"不支持的视频平台: {url}")
        
        # 生成输出文件名
        video_id = self._extract_video_id(url, platform)
        output_path = os.path.join(self.output_dir, f"{video_id}.mp4")
        
        # 下载配置
        ydl_opts = {
            'format': 'best[height<=720]/best',  # 720p或最佳质量
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [lambda d: self._progress_hook(d, progress_callback)],
        }
        
        # 针对不同平台的特殊配置
        if platform == 'bilibili':
            ydl_opts['http_headers'] = {
                'Referer': 'https://www.bilibili.com',
            }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # 获取实际下载的文件路径
                if os.path.exists(output_path):
                    final_path = output_path
                else:
                    # yt-dlp可能会更改文件扩展名
                    for ext in ['.mp4', '.webm', '.mkv']:
                        test_path = output_path.replace('.mp4', ext)
                        if os.path.exists(test_path):
                            final_path = test_path
                            break
                    else:
                        final_path = output_path
                
                return {
                    'success': True,
                    'file_path': final_path,
                    'file_size': os.path.getsize(final_path) if os.path.exists(final_path) else 0,
                    'video_info': {
                        'title': info.get('title', ''),
                        'description': info.get('description', ''),
                        'duration': info.get('duration', 0),
                        'thumbnail': info.get('thumbnail', ''),
                    }
                }
        except Exception as e:
            logger.error(f"下载视频失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_video_id(self, url: str, platform: str) -> str:
        """提取视频ID"""
        parsed = urlparse(url)
        path = parsed.path

        # 根据平台提取ID
        if platform == 'douyin':
            match = re.search(r'/video/(\d+)', path)
            if match:
                return match.group(1)
        elif platform == 'bilibili':
            match = re.search(r'/video/(BV\w+)', path)
            if match:
                return match.group(1)
        elif platform == 'youtube':
            if parsed.netloc.lower().endswith('youtu.be'):
                video_id = path.strip('/').split('/')[0]
                if video_id:
                    return video_id
            match = re.search(r'(?:^|&)v=([^&]+)', parsed.query)
            if match:
                return match.group(1)

        # 使用确定性 hash 替代内置 hash()
        return hashlib.md5(url.encode()).hexdigest()[:16]
    
    def _progress_hook(self, d: dict, callback=None):
        """下载进度回调"""
        if callback and d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                progress = int(downloaded / total * 100)
                callback(progress)
    
    def cleanup(self, file_path: str):
        """清理下载的文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"已清理文件: {file_path}")
        except Exception as e:
            logger.error(f"清理文件失败: {e}")
