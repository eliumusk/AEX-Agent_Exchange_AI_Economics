from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from ..agent_hub import BaseAgentHub
load_dotenv()

class GeneralAssitantHub(BaseAgentHub):
    """经济型通用助理Hub"""

    def __init__(self):
        super().__init__(
            name="经济通用助理",
            description="一个多面手通用助理，以较低的成本快速完成常规任务"
        )

    def get_capabilities(self) -> list:
        return ["research", "summary", "writing", "task_management"]

    def setup_team(self) -> Team:
        # 使用成本更低的模型
        model_config = self.get_model_config(model_name="gpt-3.5-turbo") 

        # 创建通用助理Agent
        general_assistant = Agent(
            name="通用助理",
            role="万能的帮手",
            goal="高效完成用户交代的各种常规性任务，如信息查询、内容摘要、邮件草拟等",
            description="我是一个任劳任怨的通用助理，也许不是每个领域最顶尖的专家，但我学习能力强，能快速上手，以最高性价比完成任务。",
            model=OpenAIChat(**model_config),
            tools=[DuckDuckGoTools()],
        )
        
        team = Team(
            name="经济速递助理团队",
            description="成本优先，快速响应",
            members=[general_assistant],
            mode="single", # 单人执行
        )
        return team