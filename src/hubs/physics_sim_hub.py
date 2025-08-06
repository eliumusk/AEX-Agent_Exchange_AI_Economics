from dotenv import load_dotenv
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat

from ..agent_hub import BaseAgentHub
load_dotenv()

class PhysicsSimHub(BaseAgentHub):
    """物理现象模拟与理论团队Hub"""
    
    def __init__(self):
        super().__init__(
            name="物理现象模拟与理论团队",
            description="专注于解决理论物理问题和进行计算物理模拟，用于探索从天体物理到量子力学的各类物理现象。"
        )
    
    def get_capabilities(self) -> list:
        """获取Hub能力列表"""
        return ["physics_simulation", "theoretical_modeling", "symbolic_math", "numerical_methods", "data_analysis"]
    
    def setup_team(self) -> Team:
        """设置物理学家团队"""
        model_config = self.get_model_config()
        
        # 创建理论物理学家Agent
        theoretical_physicist = Agent(
            name="理论物理学家",
            role="数学物理方程求解者",
            goal="建立物理现象的数学模型，并使用符号计算工具推导和求解相关的理论方程。",
            description="""
            你拥有爱因斯坦般的洞察力，擅长用优美的数学语言描述复杂的物理世界。
            无论是解薛定谔方程还是推导场方程，都是你的拿手好戏。
            """,
            model=OpenAIChat(**model_config),
            tools=[WolframAlphaTools()],
            instructions=[
                "首先将物理问题抽象成精确的数学模型。",
                "使用符号计算来寻求解析解。",
                "清晰地展示推导过程中的每一步逻辑。",
                "如果无法得到解析解，为数值计算提供简化的方程形式。"
            ],
        )
        
        # 创建计算物理学家Agent
        computational_physicist = Agent(
            name="计算物理学家",
            role="数值模拟专家",
            goal="将理论模型转化为计算机程序，通过数值方法（如有限元、蒙特卡洛）模拟物理过程并进行数据分析。",
            description="""
            你是一位编程高手，精通NumPy和SciPy，能够将复杂的微分方程变为计算机上生动的动画。
            你让理论物理的预测变得眼见为实。
            """,
            model=OpenAIChat(**model_config),
            tools=[CodeExecutionTools()],
            instructions=[
                "设计稳定且高效的数值算法来实现理论模型。",
                "进行收敛性测试，确保模拟结果的可靠性。",
                "对模拟产生的大量数据进行处理和可视化。",
                "将模拟结果与理论预测或实验数据进行对比分析。"
            ],
        )
        
        team = Team(
            name="物理模拟与理论团队",
            description="理论推导与数值模拟的完美结合，探索宇宙的奥秘。",
            members=[theoretical_physicist, computational_physicist],
            mode="coordinate",
        )
        
        return team

# ==============================================================================
# 示例：如何使用
# ==============================================================================
if __name__ == '__main__':
    # 实例化所有Hub，这将触发它们的内部团队设置
    chem_hub = ChemSynthHub()
    mat_hub = MatDesignHub()
    physics_hub = PhysicsSimHub()
    
    # 之后在您的AEX中，就可以根据任务选择这些hub实例去执行任务了
    # e.g., selected_hub = aex.choose_hub(task)
    # result = selected_hub.team.run(task)