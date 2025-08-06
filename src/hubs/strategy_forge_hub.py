"""
商业策略咨询团队Hub
"""
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from ..agent_hub import BaseAgentHub
load_dotenv()

class StrategyForgeHub(BaseAgentHub):
    """商业策略咨询团队Hub"""

    def __init__(self):
        super().__init__(
            name="战略熔炉咨询团队",
            description="提供深入的市场分析、竞品研究和商业战略规划"
        )

    def get_capabilities(self) -> list:
        return ["strategy", "market_analysis", "finance", "business_planning", "report"]

    def setup_team(self) -> Team:
        model_config = self.get_model_config(model_name="gpt-4-turbo") # 使用更强的模型

        # 创建市场分析师Agent
        market_analyst = Agent(
            name="市场分析师",
            role="行业数据专家",
            goal="收集和分析市场数据、行业报告和竞争对手动态，输出洞察",
            description="你是一位前麦肯锡分析师，对数字极度敏感，能从繁杂的数据中洞悉市场格局和未来趋势。",
            model=OpenAIChat(**model_config),
            tools=[DuckDuckGoTools()],
        )

        # 创建战略顾问Agent
        strategy_consultant = Agent(
            name="战略顾问",
            role="商业棋手",
            goal="基于市场洞察，制定可行的商业模式、市场进入策略和长期发展规划",
            description="你是一位经验丰富的战略顾问，擅长顶层设计，能够为企业在复杂的商业竞争中指明方向。",
            model=OpenAIChat(**model_config),
        )
        
        team = Team(
            name="战略熔炉咨询团队",
            description="数据驱动洞察，智慧引领战略",
            members=[market_analyst, strategy_consultant],
            mode="coordinate",
        )
        return team