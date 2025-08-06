"""
    软件开发团队Hub
"""

from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat

from ..agent_hub import BaseAgentHub
load_dotenv()

class CodeCraftersHub(BaseAgentHub):
    
    def __init__(self):
        super().__init__(
            name="代码工匠团队",
            description="专注于编写、测试和调试高质量代码的专家团队"
        )
    
    def get_capabilities(self) -> list:
        return ["coding", "debugging", "testing", "documentation", "code_review"]
    
    def setup_team(self) -> Team:
        model_config = self.get_model_config()
        
        # 创建资深开发者Agent
        senior_developer = Agent(
            name="资深开发者",
            role="软件架构师与核心开发者",
            goal="根据需求编写出结构清晰、高效且可维护的代码",
            description="""
            你是一位拥有十年经验的资深软件工程师，精通多种编程语言和设计模式。
            你写的代码不仅能完美实现功能，更追求优雅、健壮和高性能。
            """,
            model=OpenAIChat(**model_config),
            tools=[],
            instructions=[
                "严格遵循编码规范和最佳实践",
                "在编写代码前先进行简要的设计思考",
                "为核心功能编写清晰的文档注释",
                "确保代码的可扩展性"
            ],
        )
        
        # 创建QA测试工程师Agent
        qa_tester = Agent(
            name="QA测试工程师",
            role="质量保障专家",
            goal="发现代码中的潜在缺陷、漏洞和性能问题，确保软件质量",
            description="""
            你是一个像素眼级别的QA工程师，对Bug有着天生的嗅觉。你擅长设计
            全面的测试用例，覆盖各种边缘场景，是产品上线前的最后一道坚实防线。
            """,
            model=OpenAIChat(**model_config),
            tools=[],
            instructions=[
                "为核心功能编写单元测试或集成测试",
                "尝试使用各种边界值和异常输入进行测试",
                "清晰地描述你发现的每一个Bug，包括复现步骤",
                "不仅关注功能正确性，也关注代码性能和安全性"
            ],
        )
        
        # 创建团队
        team = Team(
            name="代码工匠团队",
            description="编写与测试紧密配合，打造工业级软件",
            members=[senior_developer, qa_tester],
            mode="coordinate",  # 协调执行：先开发，后测试
        )
        return team