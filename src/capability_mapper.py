"""
Capability Mapper
智能能力映射器：基于语义搜索的能力匹配
"""

import json
import importlib
import inspect
from typing import List, Dict, Any, Tuple
from pathlib import Path
from rich.console import Console

from .embedding_service import EmbeddingService
from .agent_hub import BaseAgentHub

console = Console()


class CapabilityMapper:
    """智能能力映射器"""

    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.hub_classes = self._discover_hub_classes()
        self.capability_descriptions = self._build_dynamic_capability_descriptions()
        self.capability_keywords = self._load_capability_keywords()

    def _discover_hub_classes(self) -> Dict[str, type]:
        """动态发现所有Hub类"""
        hub_classes = {}
        try:
            # 获取hubs目录路径
            hubs_dir = Path(__file__).parent / "hubs"

            if not hubs_dir.exists():
                console.print("[yellow]警告: hubs目录不存在[/yellow]")
                return hub_classes

            # 扫描所有Python文件
            for py_file in hubs_dir.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue

                module_name = py_file.stem
                try:
                    # 动态导入模块
                    module = importlib.import_module(f"src.hubs.{module_name}")

                    # 查找继承自BaseAgentHub的类
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (obj != BaseAgentHub and
                            issubclass(obj, BaseAgentHub) and
                            obj.__module__ == module.__name__):

                            hub_classes[name] = obj

                except Exception as e:
                    console.print(f"[yellow]导入模块 {module_name} 失败: {e}[/yellow]")

        except Exception as e:
            console.print(f"[red]扫描Hub类失败: {e}[/red]")

        return hub_classes

    def _build_dynamic_capability_descriptions(self) -> Dict[str, str]:
        """动态构建能力描述"""
        descriptions = {}

        # 从所有Hub类中收集能力和描述
        for hub_class_name, hub_class in self.hub_classes.items():
            try:
                # 创建Hub实例来获取能力和描述
                hub_instance = hub_class()
                capabilities = hub_instance.get_capabilities()
                hub_description = hub_instance.description

                # 为每个能力添加或更新描述
                for capability in capabilities:
                    if capability in descriptions:
                        # 如果能力已存在，合并描述
                        descriptions[capability] += f"; {hub_description}"
                    else:
                        # 新能力，使用Hub描述
                        descriptions[capability] = hub_description

                console.print(f"[green]从 {hub_class_name} 收集到能力: {capabilities}[/green]")

            except Exception as e:
                console.print(f"[yellow]无法从 {hub_class_name} 获取能力: {e}[/yellow]")

        # 如果没有发现任何能力，使用基础默认能力
        if not descriptions:
            console.print("[yellow]未发现任何Hub能力，使用默认能力[/yellow]")
            descriptions = {
                "research": "信息搜索、调研、资料收集、数据分析",
                "writing": "文章撰写、内容创作、文案写作、报告编写",
                "analysis": "数据分析、趋势分析、统计分析、内容分析",
                "technical": "技术咨询、技术支持、技术分析、架构设计"
            }

        console.print(f"[cyan]动态构建了 {len(descriptions)} 个能力描述[/cyan]")
        return descriptions
    
    def _load_capability_keywords(self) -> Dict[str, List[str]]:
        """加载基础关键词（作为备用方案）"""
        # 只保留最基本的关键词作为备用
        keywords = {
            "research": ["调研", "研究", "搜索", "查找", "了解", "分析"],
            "writing": ["写", "撰写", "生成", "创作", "编写"],
            "technical": ["技术", "代码", "编程", "开发"],
            "analysis": ["分析", "统计", "数据"]
        }
        return keywords

    def display_discovered_capabilities(self):
        """显示动态发现的能力"""
        if self.capability_descriptions:
            console.print(f"\n[cyan]动态发现的能力 ({len(self.capability_descriptions)}个):[/cyan]")
            for capability, description in self.capability_descriptions.items():
                # 截断过长的描述
                short_desc = description[:80] + "..." if len(description) > 80 else description
                console.print(f"  • [bold]{capability}[/bold]: {short_desc}")
        else:
            console.print("[yellow]未发现任何能力[/yellow]")

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
