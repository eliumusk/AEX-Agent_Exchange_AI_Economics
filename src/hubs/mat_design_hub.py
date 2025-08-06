from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat

from ..agent_hub import BaseAgentHub
load_dotenv()

class MatDesignHub(BaseAgentHub):
    """新材料设计与模拟团队Hub"""
    
    def __init__(self):
        super().__init__(
            name="新材料设计与模拟团队",
            description="结合材料信息学与计算模拟，用于设计具有特定性能的新材料，并预测其在各种条件下的行为。"
        )
    
    def get_capabilities(self) -> list:
        """获取Hub能力列表"""
        return ["materials_design", "property_prediction", "simulation", "data_analysis", "materials_informatics"]
    
    def setup_team(self) -> Team:
        """设置材料科学家团队"""
        model_config = self.get_model_config()
        
        # 创建材料信息学专家Agent
        materials_informatics_expert = Agent(
            name="材料信息学专家",
            role="材料基因组工程师",
            goal="利用机器学习和材料数据库（如Materials Project）高通量筛选具有目标性能的候选材料。",
            description="""
            你是一位前沿的材料信息学专家，擅长从海量材料数据中发现规律。
            你可以通过数据驱动的方法，快速缩小潜在新材料的搜索范围。
            """,
            model=OpenAIChat(**model_config),
            tools=[],
            instructions=[
                "明确定义目标性能作为筛选标准。",
                "使用机器学习模型预测没有实验数据的材料属性。",
                "提供候选材料的晶体结构、能带图等关键信息。",
                "解释筛选结果背后的物理或化学原理。"
            ],
        )
        
        # 创建模拟工程师Agent
        simulation_engineer = Agent(
            name="模拟工程师",
            role="计算材料科学家",
            goal="对候选材料进行原子级别的模拟（如分子动力学MD），以验证其在特定工况下的性能和稳定性。",
            description="""
            你精通LAMMPS、VASP等模拟软件，可以在原子尺度上重现材料在受力、受热时的动态行为。
            你的模拟结果是连接理论设计和宏观实验的关键桥梁。
            """,
            model=OpenAIChat(**model_config),
            tools=[],
            instructions=[
                "根据候选材料的结构建立精确的原子模型。",
                "选择合适的力场或势函数进行模拟。",
                "模拟材料在高温、高压、拉伸等不同条件下的响应。",
                "分析模拟轨迹，计算力学性能、热导率等宏观属性。"
            ],
        )
        
        team = Team(
            name="新材料设计团队",
            description="数据筛选与物理模拟相结合，加速新材料的研发进程。",
            members=[materials_informatics_expert, simulation_engineer],
            mode="coordinate", # 协调执行：先筛选，后模拟
        )
        
        return team