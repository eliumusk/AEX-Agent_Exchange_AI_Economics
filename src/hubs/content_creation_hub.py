"""
Content Creation Hub
内容创作团队：专注于信息研究和高质量内容撰写
"""
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

from ..agent_hub import BaseAgentHub
load_dotenv()

class ContentCreationHub(BaseAgentHub):
    """内容创作团队Hub"""
    
    def __init__(self):
        super().__init__(
            name="内容创作团队",
            description="专注于信息研究和高质量内容撰写的智能体团队"
        )
    
    def get_capabilities(self) -> list:
        """获取Hub能力列表"""
        return ["research", "writing", "summary", "analysis", "report"]
    
    def setup_team(self) -> Team:
        """设置内容创作团队"""
        # 获取模型配置
        model_config = self.get_model_config()
        
        # 创建研究员Agent
        researcher = Agent(
            name="研究员",
            role="信息研究专家",
            goal="收集、分析和整理相关信息，为内容创作提供准确的数据支持",
            description="""
            你是一位经验丰富的研究员，擅长从各种来源收集信息，
            进行深入分析，并能够识别可靠的信息源。你总是确保
            信息的准确性和时效性，为团队提供高质量的研究基础。
            """,
            model=OpenAIChat(**model_config),
            tools=[DuckDuckGoTools()],
            instructions=[
                "始终使用最新和可靠的信息源",
                "提供详细的研究结果和数据支持",
                "标注信息来源和时间",
                "识别关键趋势和模式",
                "确保信息的客观性和准确性"
            ],
        )
        
        # 创建作家Agent
        writer = Agent(
            name="作家",
            role="内容创作专家",
            goal="基于研究结果创作高质量、结构清晰、易于理解的内容",
            description="""
            你是一位专业的内容创作者，擅长将复杂的信息转化为
            清晰、引人入胜的文章。你具有出色的写作技巧，能够
            根据不同的受众调整写作风格，确保内容既专业又易懂。
            """,
            model=OpenAIChat(**model_config),
            instructions=[
                "创作结构清晰、逻辑严密的内容",
                "使用简洁明了的语言",
                "确保内容的可读性和吸引力",
                "包含适当的标题和段落结构",
                "基于研究结果进行创作，确保准确性"
            ],
        )
        
        # 创建团队
        team = Team(
            name="内容创作团队",
            description="专业的研究和写作团队，致力于创作高质量内容",
            members=[researcher, writer],
            mode="sequential",  # 顺序执行：先研究，后写作
            show_members_responses=True,
            show_tool_calls=True,
            markdown=True,
            memory=True
        )
        
        return team
