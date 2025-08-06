"""
Agent Hub Base Classes
智能体中心基础类：定义Hub的抽象接口和通用功能
"""

import os
from abc import ABC, abstractmethod
from typing import Any, Optional
from rich.console import Console

console = Console()


class BaseAgentHub(ABC):
    """Agent Hub抽象基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.team = None
        self._initialized = False
    
    @abstractmethod
    def setup_team(self) -> Any:
        """设置团队 - 子类必须实现"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> list:
        """获取Hub能力列表 - 子类必须实现"""
        pass
    
    def initialize(self) -> bool:
        """初始化Hub"""
        try:
            if not self._initialized:
                self.team = self.setup_team()
                self._initialized = True
                console.print(f"[green]Hub '{self.name}' 初始化成功[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Hub '{self.name}' 初始化失败: {e}[/red]")
            return False
    
    def run(self, task: str) -> Optional[str]:
        """执行任务"""
        try:
            # 确保Hub已初始化
            if not self.initialize():
                return None

            console.print(f"[blue]Hub '{self.name}' 开始执行任务[/blue]")

            # 使用agno team的print_response方法
            print(f"\n{'='*60}")
            print(f"🤖 {self.name} 正在处理您的任务...")
            print(f"{'='*60}\n")

            # 执行任务并直接打印响应
            self.team.print_response(task, stream=True)

            console.print(f"\n[green]Hub '{self.name}' 任务执行完成[/green]")

            # 返回一个简单的完成消息，因为实际结果已经通过print_response输出了
            return "任务已完成，详细结果请查看上方输出。"

        except Exception as e:
            console.print(f"[red]Hub '{self.name}' 执行任务时出错: {e}[/red]")
            return None
    
    async def arun(self, task: str) -> Optional[str]:
        """异步执行任务"""
        try:
            # 确保Hub已初始化
            if not self.initialize():
                return None
            
            console.print(f"[blue]Hub '{self.name}' 开始异步执行任务[/blue]")
            
            # 异步执行任务
            result = await self.team.arun(task)
            
            console.print(f"[green]Hub '{self.name}' 异步任务执行完成[/green]")
            return result
            
        except Exception as e:
            console.print(f"[red]Hub '{self.name}' 异步执行任务时出错: {e}[/red]")
            return None
    
    def get_model_config(self) -> dict:
        """获取模型配置"""
        return {
            "id": os.getenv("OPENAI_MODEL", "gpt-4o"),
            "api_key": os.getenv("OPENAI_API_KEY"),
            "base_url": os.getenv("OPENAI_BASE_URL")
        }
    
    def __str__(self) -> str:
        return f"Hub(name='{self.name}', description='{self.description}')"
    
    def __repr__(self) -> str:
        return self.__str__()
