"""
USP - User-Side Platform
用户端平台：处理CLI输入、任务解析和智能能力映射
"""

import re
from typing import List, Dict, Any
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from .embedding_service import EmbeddingService
from .capability_mapper import CapabilityMapper

console = Console()


class TaskRequest:
    """任务请求对象"""
    
    def __init__(self, original_prompt: str, required_capabilities: List[str]):
        self.original_prompt = original_prompt
        self.required_capabilities = required_capabilities
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_prompt": self.original_prompt,
            "required_capabilities": self.required_capabilities
        }


class UserSidePlatform:
    """用户端平台 - 处理用户输入和任务解析"""

    def __init__(self, use_semantic_search: bool = True):
        self.use_semantic_search = use_semantic_search

        # 初始化嵌入服务和能力映射器
        if use_semantic_search:
            try:
                self.embedding_service = EmbeddingService()
                self.capability_mapper = CapabilityMapper(self.embedding_service)
                console.print("[green]智能语义搜索已启用[/green]")
            except Exception as e:
                console.print(f"[yellow]语义搜索初始化失败，使用关键词匹配: {e}[/yellow]")
                self.use_semantic_search = False
                self.capability_mapper = None

        # 关键词到能力的映射（备用方案）
        self.keyword_to_capability = {
            # 研究相关
            "调研": "research",
            "研究": "research",
            "搜索": "research",
            "查找": "research",
            "写": "writing",
            "生成": "writing",
            "总结": "summary",
            "报告": "report",
            "代码": "coding",

        }
    
    def get_user_input(self) -> str:
        """获取用户输入的任务"""
        console.print(Panel.fit(
            "[bold blue]AEX - 动态智能体市场[/bold blue]\n"
            "请描述您需要完成的任务，我们将为您匹配最合适的智能体团队。",
            title="欢迎使用 AEX",
            border_style="blue"
        ))
        
        task = Prompt.ask(
            "\n[bold green]请输入您的任务[/bold green]",
            default="请帮我调研一下2025年AI Agent技术的发展趋势，并生成一份总结报告"
        )
        
        return task.strip()
    
    def extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        keywords = []
        text_lower = text.lower()
        
        for keyword, capability in self.keyword_to_capability.items():
            if keyword in text_lower:
                keywords.append(keyword)
        
        return keywords
    
    def map_to_capabilities(self, keywords: List[str]) -> List[str]:
        """将关键词映射到标准能力"""
        capabilities = set()
        
        for keyword in keywords:
            if keyword in self.keyword_to_capability:
                capabilities.add(self.keyword_to_capability[keyword])
        
        # 如果没有匹配到任何能力，使用默认的通用能力
        if not capabilities:
            # 简单的启发式规则
            text_lower = " ".join(keywords).lower() if keywords else ""
            if any(word in text_lower for word in ["写", "生成", "创作", "撰写"]):
                capabilities.add("writing")
            if any(word in text_lower for word in ["研究", "调研", "分析", "了解"]):
                capabilities.add("research")
            
            # 如果还是没有，默认为研究和写作
            if not capabilities:
                capabilities.update(["research", "writing"])
        
        return list(capabilities)
    
    def create_task_request(self, user_input: str) -> TaskRequest:
        """创建任务请求对象"""
        if self.use_semantic_search and self.capability_mapper:
            # 使用智能语义搜索
            console.print("[cyan]使用智能语义搜索分析任务...[/cyan]")
            capabilities = self.capability_mapper.extract_capabilities(user_input)

            # 显示解析结果
            console.print(f"\n[dim]语义分析结果: {capabilities}[/dim]")

            # 显示能力描述
            for cap in capabilities:
                desc = self.capability_mapper.get_capability_description(cap)
                console.print(f"[dim]  • {cap}: {desc[:50]}...[/dim]")
        else:
            # 使用传统关键词匹配
            console.print("[yellow]使用关键词匹配分析任务...[/yellow]")
            keywords = self.extract_keywords(user_input)
            capabilities = self.map_to_capabilities(keywords)

            # 显示解析结果
            console.print(f"\n[dim]检测到的关键词: {keywords}[/dim]")
            console.print(f"[dim]映射到的能力: {capabilities}[/dim]")

        return TaskRequest(user_input, capabilities)
    
    def display_task_info(self, task_request: TaskRequest):
        """显示任务信息"""
        console.print(Panel(
            f"[bold]原始任务:[/bold] {task_request.original_prompt}\n"
            f"[bold]所需能力:[/bold] {', '.join(task_request.required_capabilities)}",
            title="任务解析结果",
            border_style="green"
        ))
