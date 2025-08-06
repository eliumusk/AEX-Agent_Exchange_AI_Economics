#!/usr/bin/env python3
"""
AEX - Agent Exchange MVP
动态智能体市场主程序

基于《Agent Exchange》论文的核心思想，实现一个可以真实运行的
最小化原型，将AI智能体从被动工具转变为能够参与市场化选择的经济参与者。
"""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.traceback import install

# 安装rich的traceback处理
install()

# 加载环境变量
load_dotenv()

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.usp import UserSidePlatform
from src.aex import AgentExchange

console = Console()


def check_environment() -> bool:
    """检查环境配置"""
    required_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        console.print(Panel(
            f"[red]缺少必要的环境变量:[/red]\n" + 
            "\n".join(f"• {var}" for var in missing_vars) +
            "\n\n请检查 .env 文件配置",
            title="环境配置错误",
            border_style="red"
        ))
        return False
    
    return True


def display_welcome():
    """显示欢迎信息"""
    welcome_text = """
[bold blue]AEX - 动态智能体市场[/bold blue]

本系统将AI智能体视为能够参与市场化选择的"经济参与者"。

[bold green]系统功能:[/bold green]
• 智能任务解析和能力匹配
• 动态智能体团队选择
• 真实任务执行和结果返回

    """
    
    console.print(Panel(
        welcome_text,
        title="欢迎使用 AEX",
        border_style="blue",
        padding=(1, 2)
    ))


def main():
    """主程序入口"""
    try:
        # 显示欢迎信息
        display_welcome()
        
        # 检查环境配置
        if not check_environment():
            return 1
        
        # 初始化组件
        use_semantic = os.getenv("USE_SEMANTIC_SEARCH", "true").lower() == "true"
        usp = UserSidePlatform(use_semantic_search=use_semantic)
        aex = AgentExchange()
        
        console.print("[green]系统初始化完成[/green]\n")
        
        while True:
            try:
                # 1. 获取用户输入
                user_input = usp.get_user_input()
                
                if not user_input or user_input.lower() in ['quit', 'exit', '退出']:
                    console.print("\n[yellow]感谢使用 AEX！再见！[/yellow]")
                    break
                
                # 2. 创建任务请求
                task_request = usp.create_task_request(user_input)
                usp.display_task_info(task_request)
                
                # 3. 执行任务
                result = aex.execute_task(task_request)
                
                # 4. 显示结果
                if result:
                    console.print(f"\n[green]✅ {result}[/green]")
                else:
                    console.print(Panel(
                        "[red]任务执行失败，请检查配置或重试[/red]",
                        title="执行失败",
                        border_style="red"
                    ))
                
                # 询问是否继续
                console.print("\n" + "="*60 + "\n")
                continue_choice = console.input("[bold cyan]是否继续执行新任务？(y/n): [/bold cyan]")
                if continue_choice.lower() not in ['y', 'yes', '是', '继续']:
                    console.print("\n[yellow]感谢使用 AEX！再见！[/yellow]")
                    break
                
                console.print("\n")
                
            except KeyboardInterrupt:
                console.print("\n\n[yellow]用户中断，正在退出...[/yellow]")
                break
            except Exception as e:
                console.print(f"\n[red]发生错误: {e}[/red]")
                console.print("[yellow]请重试或输入 'quit' 退出[/yellow]\n")
                continue
        
        return 0
        
    except Exception as e:
        console.print(f"[red]系统启动失败: {e}[/red]")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
