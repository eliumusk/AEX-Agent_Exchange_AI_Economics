"""
Tech Analysis Hub
技术分析团队：专注于代码分析、执行和技术问题解决
"""
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat

from ..agent_hub import BaseAgentHub
load_dotenv()

class TechAnalysisHub(BaseAgentHub):
    """技术分析团队Hub"""
    
    def __init__(self):
        super().__init__(
            name="技术分析团队",
            description="专注于代码分析、执行和技术问题解决的智能体团队"
        )
    
    def get_capabilities(self) -> list:
        """获取Hub能力列表"""
        return ["coding", "data_analysis", "debugging", "optimization", "technical"]
    
    def setup_team(self) -> Team:
        """设置技术分析团队"""
        # 获取模型配置
        model_config = self.get_model_config()
        
        # 创建代码分析师Agent
        code_analyst = Agent(
            name="代码分析师",
            role="代码分析和架构专家",
            goal="分析代码结构、识别问题、提供优化建议和技术解决方案",
            description="""
            你是一位资深的软件工程师和代码分析专家，拥有多年的
            编程经验。你擅长分析各种编程语言的代码，能够快速
            识别性能瓶颈、安全问题和架构缺陷，并提供实用的
            优化建议。
            """,
            model=OpenAIChat(**model_config),
            instructions=[
                "仔细分析代码的结构和逻辑",
                "识别潜在的性能问题和安全风险",
                "提供具体的优化建议和最佳实践",
                "解释技术概念时使用清晰的语言",
                "提供可执行的代码示例和解决方案"
            ],
            
        )
        
        # 创建技术顾问Agent
        tech_consultant = Agent(
            name="技术顾问",
            role="技术咨询和解决方案专家",
            goal="提供技术咨询、解决复杂技术问题、推荐技术栈和工具",
            description="""
            你是一位经验丰富的技术顾问，对各种技术栈、框架
            和工具都有深入的了解。你能够根据具体需求推荐
            最适合的技术解决方案，并帮助团队做出明智的
            技术决策。
            """,
            model=OpenAIChat(**model_config),
            instructions=[
                "基于具体需求提供技术建议",
                "推荐合适的工具和技术栈",
                "考虑可维护性、可扩展性和性能",
                "提供实施步骤和注意事项",
                "保持技术建议的实用性和可行性"
            ],

        )
        
        # 创建团队
        team = Team(
            name="技术分析团队",
            description="专业的技术分析和咨询团队，解决各种技术问题",
            members=[code_analyst, tech_consultant],
            mode="collaborative",  # 协作模式：由主agent进行分配
            memory=True,
            show_members_responses=True,
            show_tool_calls=True,
            markdown=True,
        )
        
        return team
