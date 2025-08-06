from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat

from ..agent_hub import BaseAgentHub
load_dotenv()

class ChemSynthHub(BaseAgentHub):
    """化学合成路径规划团队Hub"""
    
    def __init__(self):
        super().__init__(
            name="化学合成路径规划团队",
            description="专注于计算化学模拟和文献挖掘，用于预测化学反应、设计分子结构和规划最优合成路径。"
        )
    
    def get_capabilities(self) -> list:
        """获取Hub能力列表"""
        return ["synthesis_planning", "computational_chemistry", "literature_search", "molecular_analysis", "reaction_prediction"]
    
    def setup_team(self) -> Team:
        """设置化学家团队"""
        model_config = self.get_model_config()
        
        # 创建文献化学家Agent
        literature_chemist = Agent(
            name="文献化学家",
            role="化学知识库检索专家",
            goal="从公共数据库和文献中检索已知化合物的性质、反应条件和合成路线。",
            description="""
            你是一位经验丰富的有机化学家，精通使用PubChem, Reaxys等数据库。
            你能够快速定位目标分子的关键信息，为新的合成实验提供坚实的文献基础。
            """,
            model=OpenAIChat(**model_config),
            tools=[],
            instructions=[
                "优先使用专业的化学数据库进行查询。",
                "交叉验证多个来源的信息以确保准确性。",
                "不仅关注产物，还要关注反应的收率、副产物和安全注意事项。",
                "为后续的计算模拟提供关键的输入参数。"
            ],
        )
        
        # 创建计算化学家Agent
        computational_chemist = Agent(
            name="计算化学家",
            role="分子模拟与量子化学专家",
            goal="使用计算工具模拟分子结构，预测反应活性、能垒和光谱性质，从而指导实验设计。",
            description="""
            你擅长运用量子化学和分子动力学原理，通过软件（如RDKit, PySCF）构建虚拟化学实验。
            你可以在计算机上预测反应的可行性，有效减少昂贵且耗时的实体实验。
            """,
            model=OpenAIChat(**model_config),
            tools=[],
            instructions=[
                "根据文献化学家提供的信息建立准确的分子模型。",
                "选择合适的计算方法和基组以平衡精度和效率。",
                "清晰地解释你的计算结果，包括能量图、轨道分析等。",
                "基于模拟结果，提出具体的、可操作的合成路线建议。"
            ],
        )
        
        # 创建团队
        team = Team(
            name="化学合成团队",
            description="文献挖掘与计算模拟双剑合璧，高效设计化学合成方案。",
            members=[literature_chemist, computational_chemist],
            mode="coordinate",  # 协调执行：先查文献，后模拟计算
        )
        
        return team