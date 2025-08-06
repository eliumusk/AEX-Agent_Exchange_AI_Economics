"""
Capability Mapper
智能能力映射器：基于语义搜索的能力匹配
"""

import json
from typing import List, Dict, Any, Tuple
from pathlib import Path
from rich.console import Console

from .embedding_service import EmbeddingService

console = Console()


class CapabilityMapper:
    """智能能力映射器"""
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.capability_descriptions = self._load_capability_descriptions()
        self.capability_keywords = self._load_capability_keywords()
        
    def _load_capability_descriptions(self) -> Dict[str, str]:
        """加载能力描述"""
        descriptions = {
            # 研究相关
            "research": "信息搜索、调研、资料收集、数据分析、市场研究、学术研究、背景调查",
            "analysis": "数据分析、趋势分析、统计分析、内容分析、比较分析、深度分析",
            
            # 写作相关  
            "writing": "文章撰写、内容创作、文案写作、报告编写、博客写作、创意写作",
            "summary": "内容总结、摘要提取、要点归纳、信息整理、精华提炼",
            "report": "报告生成、文档制作、方案撰写、总结报告、分析报告",
            
            # 技术相关
            "coding": "编程开发、代码编写、软件开发、脚本编写、算法实现、程序设计",
            "debugging": "代码调试、错误修复、问题诊断、bug修复、程序调试",
            "optimization": "性能优化、代码优化、系统优化、效率提升、速度优化",
            "technical": "技术咨询、技术支持、技术分析、架构设计、技术方案",
            "data_analysis": "数据处理、数据挖掘、数据可视化、统计分析、数据科学",
            
            # 测试相关
            "test": "软件测试、功能测试、性能测试、自动化测试、测试用例设计",
            "demo": "演示制作、原型开发、概念验证、示例创建、展示设计",
            "example": "示例代码、使用案例、教程制作、样例开发、参考实现",
            
            # 创意相关
            "creative": "创意设计、艺术创作、创新思维、概念设计、视觉设计",
            "design": "界面设计、用户体验、产品设计、视觉设计、交互设计",
            
            # 商业相关
            "business": "商业分析、市场策略、商业计划、竞争分析、商业咨询",
            "marketing": "市场营销、品牌推广、营销策略、广告创意、社交媒体",
            
            # 教育相关
            "education": "教学设计、课程开发、培训材料、学习指导、知识传授",
            "tutorial": "教程制作、指导文档、学习资料、操作指南、培训内容"
        }
        return descriptions
    
    def _load_capability_keywords(self) -> Dict[str, List[str]]:
        """加载能力关键词（作为备用方案）"""
        keywords = {
            "research": ["调研", "研究", "搜索", "查找", "了解", "分析", "调查"],
            "writing": ["写", "撰写", "生成", "创作", "编写", "写作"],
            "summary": ["总结", "汇总", "概括", "整理", "归纳"],
            "report": ["报告", "文档", "方案", "总结报告"],
            "coding": ["代码", "编程", "开发", "程序", "算法"],
            "debugging": ["调试", "修复", "错误", "bug"],
            "optimization": ["优化", "性能", "提升", "改进"],
            "technical": ["技术", "架构", "系统", "工程"],
            "data_analysis": ["数据", "统计", "分析", "挖掘"],
            "test": ["测试", "验证", "检验"],
            "demo": ["演示", "展示", "原型"],
            "example": ["示例", "例子", "案例", "样例"]
        }
        return keywords
    
    def extract_capabilities_semantic(self, task_text: str, threshold: float = 0.3) -> List[str]:
        """使用语义搜索提取能力"""
        try:
            # 获取所有能力描述
            capability_texts = []
            capability_names = []
            
            for capability, description in self.capability_descriptions.items():
                capability_texts.append(description)
                capability_names.append(capability)
            
            # 找到最相似的能力
            similarities = self.embedding_service.find_most_similar(
                task_text, capability_texts, top_k=len(capability_texts)
            )
            
            # 筛选超过阈值的能力
            matched_capabilities = []
            for text, similarity in similarities:
                if similarity >= threshold:
                    # 找到对应的能力名称
                    for i, desc in enumerate(capability_texts):
                        if desc == text:
                            capability_name = capability_names[i]
                            matched_capabilities.append(capability_name)
                            console.print(f"[dim]语义匹配: {capability_name} (相似度: {similarity:.3f})[/dim]")
                            break
            
            return matched_capabilities
            
        except Exception as e:
            console.print(f"[yellow]语义搜索失败，使用关键词匹配: {e}[/yellow]")
            return self.extract_capabilities_keywords(task_text)
    
    def extract_capabilities_keywords(self, task_text: str) -> List[str]:
        """使用关键词匹配提取能力（备用方案）"""
        matched_capabilities = set()
        task_lower = task_text.lower()
        
        for capability, keywords in self.capability_keywords.items():
            for keyword in keywords:
                if keyword in task_lower:
                    matched_capabilities.add(capability)
                    break
        
        # 如果没有匹配到任何能力，使用默认能力
        if not matched_capabilities:
            # 简单的启发式规则
            if any(word in task_lower for word in ["写", "生成", "创作", "撰写"]):
                matched_capabilities.add("writing")
            if any(word in task_lower for word in ["研究", "调研", "分析", "了解"]):
                matched_capabilities.add("research")
            
            # 如果还是没有，默认为研究和写作
            if not matched_capabilities:
                matched_capabilities.update(["research", "writing"])
        
        return list(matched_capabilities)
    
    def extract_capabilities(self, task_text: str, use_semantic: bool = True) -> List[str]:
        """提取任务所需的能力"""
        if use_semantic:
            semantic_capabilities = self.extract_capabilities_semantic(task_text)
            if semantic_capabilities:
                return semantic_capabilities
        
        # 回退到关键词匹配
        return self.extract_capabilities_keywords(task_text)
    
    def get_capability_description(self, capability: str) -> str:
        """获取能力描述"""
        return self.capability_descriptions.get(capability, capability)
    
    def add_capability(self, name: str, description: str, keywords: List[str] = None):
        """添加新的能力"""
        self.capability_descriptions[name] = description
        if keywords:
            self.capability_keywords[name] = keywords
        
        console.print(f"[green]添加新能力: {name}[/green]")
    
    def save_capabilities(self, file_path: str = "cache/capabilities.json"):
        """保存能力配置"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                "descriptions": self.capability_descriptions,
                "keywords": self.capability_keywords
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            console.print(f"[green]能力配置已保存到 {file_path}[/green]")
            
        except Exception as e:
            console.print(f"[red]保存能力配置失败: {e}[/red]")
    
    def load_capabilities(self, file_path: str = "cache/capabilities.json"):
        """加载能力配置"""
        try:
            if Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if "descriptions" in config:
                    self.capability_descriptions.update(config["descriptions"])
                if "keywords" in config:
                    self.capability_keywords.update(config["keywords"])
                
                console.print(f"[green]从 {file_path} 加载了能力配置[/green]")
                
        except Exception as e:
            console.print(f"[yellow]加载能力配置失败: {e}[/yellow]")
