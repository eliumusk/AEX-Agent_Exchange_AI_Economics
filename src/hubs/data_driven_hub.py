"""
数据科学分析团队
"""
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools.calculator import CalculatorTools
from agno.tools.python import PythonTools
from ..agent_hub import BaseAgentHub
load_dotenv()

class DataDrivenHub(BaseAgentHub):
    """数据科学分析团队Hub"""

    def __init__(self):
        super().__init__(
            name="数据驱动团队",
            description="专业的数据处理、分析和可视化团队，将数据转化为业务洞察"
        )

    def get_capabilities(self) -> list:
        return ["data_analysis", "visualization", "python", "coding", "report"]

    def setup_team(self) -> Team:
        model_config = self.get_model_config()

        # 创建数据清洗师Agent
        data_wrangler = Agent(
            name="数据清洗师",
            role="数据整理专家",
            goal="处理原始数据，包括清洗、格式转换、缺失值处理，为后续分析做准备",
            description="你是一个有数据洁癖的工程师，无法容忍任何脏数据。你会用Python脚本高效地把混乱的数据变得井井有条。",
            model=OpenAIChat(**model_config),
            tools=[PythonTools(), CalculatorTools()],
        )

        # 创建数据分析与可视化工程师Agent
        data_analyst_visualizer = Agent(
            name="数据分析与可视化工程师",
            role="数据故事讲述者",
            goal="使用统计学方法和可视化工具分析数据，发现其中规律，并以图表形式清晰地呈现出来",
            description="你精通Pandas, Matplotlib, Seaborn等库，能让冰冷的数据通过精美的图表自己说话，揭示背后的故事。",
            model=OpenAIChat(**model_config),
            tools=[PythonTools(), CalculatorTools()],
        )

        team = Team(
            name="数据驱动团队",
            description="从数据清洗到可视化报告，一站式解决",
            members=[data_wrangler, data_analyst_visualizer],
            mode="coordinate",
        )
        return team