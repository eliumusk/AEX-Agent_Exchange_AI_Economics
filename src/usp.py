"""
USP - User-Side Platform
用户端平台：处理CLI输入、任务解析和关键词提取
"""

import re
from typing import List, Dict, Any
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

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
    
    def __init__(self):
        # 关键词到能力的映射
        self.keyword_to_capability = {
            # 研究相关
            "调研": "research",
            "研究": "research", 
            "分析": "analysis",
            "搜索": "research",
            "查找": "research",
            "了解": "research",
            
            # 写作相关
            "写": "writing",
            "撰写": "writing",
            "生成": "writing",
            "创作": "writing",
            "编写": "writing",
            
            # 总结相关
            "总结": "summary",
            "汇总": "summary",
            "概括": "summary",
            "整理": "summary",
            
            # 报告相关
            "报告": "report",
            "文档": "report",
            "方案": "report",
            
            # 技术相关
            "代码": "coding",
            "编程": "coding",
            "开发": "coding",
            "程序": "coding",
            "算法": "coding",
            "调试": "debugging",
            "优化": "optimization",
            "性能": "optimization",
            "技术": "technical",
            "数据": "data_analysis"
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
        # 提取关键词
        keywords = self.extract_keywords(user_input)
        
        # 映射到能力
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
