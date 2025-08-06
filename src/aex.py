"""
AEX - Agent Exchange
代理交换平台：核心逻辑控制器，负责Hub选择和任务协调
"""

import json
import os
import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .usp import TaskRequest
from .agent_hub import BaseAgentHub

console = Console()


class HubInfo:
    """Hub信息类"""
    
    def __init__(self, hub_id: str, name: str, description: str, 
                 capabilities: List[str], hub_class: str):
        self.hub_id = hub_id
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.hub_class = hub_class
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HubInfo':
        return cls(
            hub_id=data['hub_id'],
            name=data['name'],
            description=data['description'],
            capabilities=data['capabilities'],
            hub_class=data['hub_class']
        )


class AgentExchange:
    """代理交换平台 - 核心控制器"""

    def __init__(self, config_file: str = "hubs_config.json"):
        self.config_file = config_file
        self.available_hubs: List[HubInfo] = []
        self.hub_instances: Dict[str, Any] = {}
        self.hub_classes: Dict[str, type] = {}
        self._discover_hub_classes()

    def _discover_hub_classes(self):
        """自动发现所有Hub类"""
        try:
            # 获取hubs目录路径
            hubs_dir = Path(__file__).parent / "hubs"

            if not hubs_dir.exists():
                console.print("[yellow]警告: hubs目录不存在[/yellow]")
                return

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

                            self.hub_classes[name] = obj
                            console.print(f"[green]发现Hub类: {name}[/green]")

                except Exception as e:
                    console.print(f"[yellow]导入模块 {module_name} 失败: {e}[/yellow]")

        except Exception as e:
            console.print(f"[red]扫描Hub类失败: {e}[/red]")

    def display_discovered_hubs(self):
        """显示发现的Hub类"""
        if self.hub_classes:
            console.print(f"\n[cyan]发现的Hub类 ({len(self.hub_classes)}个):[/cyan]")
            for class_name in self.hub_classes.keys():
                console.print(f"  • {class_name}")
        else:
            console.print("[yellow]未发现任何Hub类[/yellow]")

    def load_hub_configs(self) -> bool:
        """加载Hub配置文件"""
        try:
            if not os.path.exists(self.config_file):
                console.print(f"[red]错误: 配置文件 {self.config_file} 不存在[/red]")
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                configs = json.load(f)
            
            self.available_hubs = [HubInfo.from_dict(config) for config in configs]
            
            console.print(f"[green]成功加载 {len(self.available_hubs)} 个Hub配置[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]加载配置文件失败: {e}[/red]")
            return False
    
    def calculate_hub_score(self, hub: HubInfo, required_capabilities: List[str]) -> float:
        """计算Hub与任务的匹配分数"""
        if not required_capabilities:
            return 0.0
        
        # 计算能力交集
        hub_capabilities = set(hub.capabilities)
        required_capabilities_set = set(required_capabilities)
        
        # 交集数量
        intersection = hub_capabilities.intersection(required_capabilities_set)
        intersection_count = len(intersection)
        
        # 基础匹配分数 (交集数量 / 所需能力数量)
        base_score = intersection_count / len(required_capabilities_set)
        
        # 覆盖率奖励 (交集数量 / Hub总能力数量)
        coverage_bonus = intersection_count / len(hub_capabilities) if hub_capabilities else 0
        
        # 完全匹配奖励
        perfect_match_bonus = 0.2 if intersection_count == len(required_capabilities_set) else 0
        
        # 最终分数
        final_score = base_score + (coverage_bonus * 0.3) + perfect_match_bonus
        
        return min(final_score, 1.0)  # 确保分数不超过1.0
    
    def select_best_hub(self, task_request: TaskRequest) -> Optional[Tuple[HubInfo, float]]:
        """选择最适合的Hub"""
        if not self.available_hubs:
            console.print("[red]没有可用的Hub[/red]")
            return None
        
        # 计算每个Hub的分数
        hub_scores = []
        for hub in self.available_hubs:
            score = self.calculate_hub_score(hub, task_request.required_capabilities)
            hub_scores.append((hub, score))
        
        # 按分数排序
        hub_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 显示选择过程
        self.display_hub_selection(hub_scores, task_request.required_capabilities)
        
        # 返回最佳Hub
        best_hub, best_score = hub_scores[0]
        
        if best_score > 0:
            return best_hub, best_score
        else:
            console.print("[yellow]警告: 没有找到完全匹配的Hub，将使用默认Hub[/yellow]")
            return hub_scores[0]  # 返回第一个Hub作为默认选择
    
    def display_hub_selection(self, hub_scores: List[Tuple[HubInfo, float]], 
                            required_capabilities: List[str]):
        """显示Hub选择过程"""
        table = Table(title="Hub匹配分析")
        table.add_column("Hub名称", style="cyan")
        table.add_column("描述", style="white")
        table.add_column("能力", style="green")
        table.add_column("匹配分数", style="yellow")
        table.add_column("状态", style="bold")
        
        for i, (hub, score) in enumerate(hub_scores):
            # 计算匹配的能力
            hub_caps = set(hub.capabilities)
            required_caps = set(required_capabilities)
            matched_caps = hub_caps.intersection(required_caps)
            
            capabilities_str = ", ".join(hub.capabilities)
            if len(capabilities_str) > 40:
                capabilities_str = capabilities_str[:37] + "..."
            
            status = "🏆 最佳匹配" if i == 0 else f"#{i+1}"
            
            table.add_row(
                hub.name,
                hub.description[:50] + "..." if len(hub.description) > 50 else hub.description,
                capabilities_str,
                f"{score:.2f}",
                status
            )
        
        console.print(table)
    
    def get_hub_instance(self, hub_info: HubInfo):
        """获取或创建Hub实例"""
        if hub_info.hub_id not in self.hub_instances:
            # 使用自动发现的Hub类
            try:
                hub_class_name = hub_info.hub_class

                if hub_class_name in self.hub_classes:
                    hub_class = self.hub_classes[hub_class_name]
                    self.hub_instances[hub_info.hub_id] = hub_class()
                    console.print(f"[green]成功创建Hub实例: {hub_class_name}[/green]")
                else:
                    console.print(f"[red]未找到Hub类: {hub_class_name}[/red]")
                    console.print(f"[yellow]可用的Hub类: {list(self.hub_classes.keys())}[/yellow]")
                    return None

            except Exception as e:
                console.print(f"[red]创建Hub实例失败 {hub_info.hub_class}: {e}[/red]")
                return None

        return self.hub_instances[hub_info.hub_id]
    
    def execute_task(self, task_request: TaskRequest) -> Optional[str]:
        """执行任务的主要流程"""
        console.print(Panel.fit(
            "[bold blue]开始任务执行流程[/bold blue]",
            border_style="blue"
        ))

        # 显示发现的Hub类
        self.display_discovered_hubs()

        # 1. 加载Hub配置
        if not self.load_hub_configs():
            return None
        
        # 2. 选择最佳Hub
        selection_result = self.select_best_hub(task_request)
        if not selection_result:
            return None
        
        best_hub, score = selection_result
        
        console.print(Panel(
            f"[bold green]选中Hub: {best_hub.name}[/bold green]\n"
            f"匹配分数: {score:.2f}\n"
            f"Hub描述: {best_hub.description}",
            title="Hub选择结果",
            border_style="green"
        ))
        
        # 3. 获取Hub实例
        hub_instance = self.get_hub_instance(best_hub)
        if not hub_instance:
            return None
        
        # 4. 执行任务
        try:
            console.print("[yellow]正在执行任务，请稍候...[/yellow]")
            result = hub_instance.run(task_request.original_prompt)
            return result
            
        except Exception as e:
            console.print(f"[red]任务执行失败: {e}[/red]")
            return None
