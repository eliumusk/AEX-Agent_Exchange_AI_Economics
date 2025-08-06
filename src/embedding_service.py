"""
Embedding Service
向量嵌入服务：使用Jina API进行语义搜索
"""

import os
import json
import pickle
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import requests
import numpy as np
from rich.console import Console

console = Console()


class EmbeddingService:
    """向量嵌入服务"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("JINA_API_KEY", "jina_1eab753c55994fe0973e7996d65e9432j_ghOOZ4ayKDNh0J4WgKZGC1Ihqt")
        self.base_url = "https://api.jina.ai/v1/embeddings"
        self.model = "jina-clip-v2"
        self.cache_dir = Path("cache/embeddings")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 向量缓存
        self.embedding_cache: Dict[str, np.ndarray] = {}
        self.load_cache()
    
    def _get_cache_key(self, text: str) -> str:
        """生成缓存键"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def load_cache(self):
        """加载缓存的向量"""
        cache_file = self.cache_dir / "embeddings.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    self.embedding_cache = pickle.load(f)
                console.print(f"[green]加载了 {len(self.embedding_cache)} 个缓存向量[/green]")
            except Exception as e:
                console.print(f"[yellow]加载向量缓存失败: {e}[/yellow]")
                self.embedding_cache = {}
    
    def save_cache(self):
        """保存向量缓存"""
        cache_file = self.cache_dir / "embeddings.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(self.embedding_cache, f)
            console.print(f"[green]保存了 {len(self.embedding_cache)} 个向量到缓存[/green]")
        except Exception as e:
            console.print(f"[yellow]保存向量缓存失败: {e}[/yellow]")
    
    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """获取文本的向量嵌入"""
        cache_key = self._get_cache_key(text)
        
        # 检查缓存
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        # 调用API获取嵌入
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "input": [{"text": text}]
            }
            
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            if "data" in result and len(result["data"]) > 0:
                embedding = np.array(result["data"][0]["embedding"])
                
                # 缓存结果
                self.embedding_cache[cache_key] = embedding
                
                return embedding
            else:
                console.print(f"[red]API返回格式错误: {result}[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]获取嵌入向量失败: {e}[/red]")
            return None
    
    def get_batch_embeddings(self, texts: List[str]) -> Dict[str, np.ndarray]:
        """批量获取文本的向量嵌入"""
        results = {}
        uncached_texts = []
        
        # 检查缓存
        for text in texts:
            cache_key = self._get_cache_key(text)
            if cache_key in self.embedding_cache:
                results[text] = self.embedding_cache[cache_key]
            else:
                uncached_texts.append(text)
        
        # 批量获取未缓存的嵌入
        if uncached_texts:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                data = {
                    "model": self.model,
                    "input": [{"text": text} for text in uncached_texts]
                }
                
                response = requests.post(self.base_url, headers=headers, json=data)
                response.raise_for_status()
                
                result = response.json()
                if "data" in result:
                    for i, item in enumerate(result["data"]):
                        if i < len(uncached_texts):
                            text = uncached_texts[i]
                            embedding = np.array(item["embedding"])
                            
                            # 缓存结果
                            cache_key = self._get_cache_key(text)
                            self.embedding_cache[cache_key] = embedding
                            results[text] = embedding
                
            except Exception as e:
                console.print(f"[red]批量获取嵌入向量失败: {e}[/red]")
        
        return results
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算余弦相似度"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception:
            return 0.0
    
    def find_most_similar(self, query_text: str, candidate_texts: List[str], 
                         top_k: int = 5) -> List[Tuple[str, float]]:
        """找到最相似的文本"""
        query_embedding = self.get_embedding(query_text)
        if query_embedding is None:
            return []
        
        # 获取候选文本的嵌入
        candidate_embeddings = self.get_batch_embeddings(candidate_texts)
        
        # 计算相似度
        similarities = []
        for text, embedding in candidate_embeddings.items():
            similarity = self.cosine_similarity(query_embedding, embedding)
            similarities.append((text, similarity))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def __del__(self):
        """析构函数，保存缓存"""
        self.save_cache()
