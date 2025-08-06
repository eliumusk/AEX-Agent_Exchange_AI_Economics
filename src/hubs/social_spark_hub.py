"""
社交媒体营销团队Hub:专注于社交媒体趋势分析、内容创意和病毒式传播
"""
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from ..agent_hub import BaseAgentHub
load_dotenv()

class SocialSparkHub(BaseAgentHub):
    """社交媒体营销团队Hub"""

    def __init__(self):
        super().__init__(
            name="社交网络火花团队",
            description="专注于社交媒体趋势分析、内容创意和病毒式传播"
        )

    def get_capabilities(self) -> list:
        return ["social_media", "trend_analysis", "content_creation", "marketing", "copywriting"]

    def setup_team(self) -> Team:
        model_config = self.get_model_config()

        # 创建趋势分析师Agent
        trend_analyst = Agent(
            name="趋势分析师",
            role="网络文化洞察者",
            goal="发现社交媒体上的热门话题、流行趋势和用户兴趣点",
            description="你是一个网络冲浪达人，对各大社交平台的热点了如指掌，能够精准预测下一个爆点。",
            model=OpenAIChat(**model_config),
            tools=[DuckDuckGoTools()],
        )

        # 创建内容创意师Agent
        content_creator = Agent(
            name="内容创意师",
            role="病毒式内容制造者",
            goal="结合热点趋势，创作能够引发用户共鸣和分享的社交媒体内容",
            description="你是一位顶级的广告文案和段子手，能用最少的文字撩动用户情绪，创造刷屏级的爆款内容。",
            model=OpenAIChat(**model_config),
        )

        team = Team(
            name="社交网络火花团队",
            description="洞察趋势，创造爆款",
            members=[trend_analyst, content_creator],
            mode="coordinate",
        )
        return team