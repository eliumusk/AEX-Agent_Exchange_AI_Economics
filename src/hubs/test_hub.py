"""
Test Hub
测试Hub：用于验证自动扫描功能
"""
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat

from ..agent_hub import BaseAgentHub

load_dotenv()


class TestHub(BaseAgentHub):
    """测试Hub"""
    
    def __init__(self):
        super().__init__(
            name="测试团队",
            description="用于测试自动扫描功能的简单团队"
        )
    
    def get_capabilities(self) -> list:
        """获取Hub能力列表"""
        return ["test", "demo", "example"]
    
    def setup_team(self) -> Team:
        """设置测试团队"""
        # 获取模型配置
        model_config = self.get_model_config()
        
        # 创建测试Agent
        test_agent = Agent(
            name="测试员",
            role="测试专家",
            goal="执行各种测试任务",
            description="你是一个测试专家，负责执行各种测试任务。",
            model=OpenAIChat(**model_config),
            instructions=[
                "执行用户要求的测试任务",
                "提供清晰的测试结果",
                "保持专业和友好的态度"
            ]
        )
        
        # 创建团队
        team = Team(
            name="测试团队",
            description="专业的测试团队",
            members=[test_agent],
            mode="coordinate",
            show_members_responses=True,
            show_tool_calls=True,
            markdown=True
        )
        
        return team
