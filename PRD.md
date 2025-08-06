### **产品需求文档 (PRD): AEX-MVP 动态智能体市场**

#### **1. 愿景与目标 (Vision & Goal)**

[cite\_start]**愿景**: 借鉴论文《Agent Exchange》的核心思想，将AI智能体从被动执行的“工具”转变为能够参与市场化选择的“经济参与者” [cite: 7]。

**MVP目标**: 构建一个可以真实运行的最小化原型。该原型需实现一个完整的核心工作流：用户提交一个任务，系统通过一个简化的市场选择机制自动挑选一个最合适的智能体团队（Agent Hub）来**真实执行**该任务，并返回最终结果。

#### **2. 核心功能与范围 (MVP Scope)**

**范围之内 (In-Scope):**

  * **1. 任务提交**: 支持用户通过命令行界面（CLI）提交一个自然语言描述的任务。
  * **2. 智能体团队注册**: 通过本地配置文件（JSON格式）手动注册几个预设的、可执行的智能体团队（Agent Hubs）。
  * **3. 团队选择机制**: 实现一个基于“能力关键词匹配”的简单算法，从已注册的团队中选择最适合执行当前任务的团队。
  * **4. 真实任务执行**: 与`Agno`智能体框架集成，调用被选中的团队（Hub）来实际运行，完成任务。
  * **5. 结果返回**: 在任务执行完毕后，将最终结果输出到命令行。

**范围之外 (Out-of-Scope):**

  * 复杂的Web用户界面（UI）。
  * 用户账户系统和持久化存储。
  * [cite\_start]论文中复杂的实时拍卖机制、多属性评估和价值归因（分钱）模块 [cite: 277, 416]。
  * [cite\_start]智能体能力的动态学习与更新 [cite: 151]。
  * [cite\_start]A2A等正式的跨智能体通信协议 [cite: 718]。

#### **3. 系统架构与组件设计 (System Architecture & Components)**

整个系统由一个主应用脚本驱动，包含以下四个核心逻辑组件的简化实现：

  * **1. 用户端平台 (USP - User-Side Platform)**

      * **MVP实现**: 一个简单的命令行输入接口。
      * **功能**: 接收用户输入的任务字符串，并提取任务的关键词用于能力匹配。
      * **技术细节**: 使用Python的`input()`函数即可。

  * **2. 代理端平台 (ASP - Agent-Side Platform)**

      * **MVP实现**: 一个本地的`hubs_config.json`配置文件。
      * **功能**: 存储所有可用的Agent Hub的信息，包括其ID、名称、所具备的能力（以关键词列表表示）以及对应的执行类名。
      * **技术细节**: 手动维护此JSON文件。

  * **3. 代理交换平台 (AEX - Agent Exchange)**

      * **MVP实现**: 项目的核心逻辑控制器，可以是一个名为`AgentExchange`的Python类。
      * **功能**:
          * 加载并解析`hubs_config.json`中的所有Hub信息。
          * 接收来自USP的任务请求。
          * 执行**选择算法**，根据任务关键词与Hub能力列表的匹配度进行评分，选出最优的Hub。
          * 实例化并触发获胜Hub的执行流程。
      * **技术细节**: 这是整个项目的指挥中心。

  * **4. 智能体中心 (Agent Hub)**

      * **MVP实现**: 每个Hub都是一个具体的Python类，该类封装了一个`Agno`的Team实例。
      * **功能**: 定义一个特定的智能体团队构成（包含哪些Agent）和他们的工作流程（Process）。接收任务输入后，负责实际的执行工作。
      * **技术细节**: 例如，可以创建`ContentCreationHub`和`TechAnalysisHub`两个类，它们内部配置了不同的`Agno`智能体。

#### **4. 技术栈与关键依赖 (Tech Stack)**

  * **语言**: Python 3.10+
  * **核心框架**: `agno` (用于构建和执行Agent Hub),官方doc我放在了[text](agno.txt)你可以查看，但是文件很大，只搜索对你有用的
  * **agno的team示例**：
```python 
from agno.team import Team
from agno.models.openai import OpenAIChat

agent_1 = Agent(name="News Agent", role="Get the latest news")

agent_2 = Agent(name="Weather Agent", role="Get the weather for the next 7 days")

team = Team(name="News and Weather Team", mode="coordinate", members=[agent_1, agent_2])

response = team.run("What is the weather in Tokyo?")

# Synchronous execution
result = team.run("What is the weather in Tokyo?")

# Asynchronous execution
result = await team.arun("What is the weather in Tokyo?")

# Streaming responses
for chunk in team.run("What is the weather in Tokyo?", stream=True):
    print(chunk.content, end="", flush=True)

# Asynchronous streaming
async for chunk in await team.arun("What is the weather in Tokyo?", stream=True):
    print(chunk.content, end="", flush=True)
```
  * **LLM依赖**: 需要配置一个大语言模型OPENROUTER的API Key，供`agno`使用。apikey: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
  * baseurl:https://openrouter.ai/api/v1
  * model:moonshotai/kimi-k2:free

#### **5. 核心工作流 (Core Workflow)**

1.  **启动**: 用户在命令行运行主程序 `main.py`。
2.  **输入**: 程序提示用户输入任务，例如："请帮我调研一下2025年AI Agent技术的发展趋势，并生成一份总结报告"。
3.  **任务解析 (USP)**: `main.py`中的USP模块提取关键词，如 `["调研", "趋势", "总结报告"]`，并映射到标准能力 `["research", "writing"]`。
4.  **加载Hubs (AEX)**: `AgentExchange`类加载`hubs_config.json`文件，了解所有可用的Hub及其能力。
5.  **选择Hub (AEX)**: `AgentExchange`将任务所需能力 `["research", "writing"]` 与每个Hub的能力进行匹配打分，最终选择得分最高的Hub（例如，`ContentCreationHub`）。
6.  **执行任务 (Agent Hub)**: `AgentExchange`实例化被选中的`ContentCreationHub`类，将原始任务字符串传递给它，并调用其执行方法（如`.run()`）。该方法内部会触发`team.run`。
7.  **返回结果**: `Agno`团队执行任务，通过联网搜索、内容生成等步骤，最终产出报告。
8.  **输出**: `main.py`将最终报告结果打印到用户的命令行。

#### **6. 数据结构定义 (Data Structures)**

**1. `hubs_config.json` 文件结构:**

```json
[
  {
    "hub_id": "content_creation_hub",
    "name": "内容创作团队",
    "description": "专注于信息研究和高质量内容撰写。",
    "capabilities": ["research", "writing", "summary"],
    "hub_name": "ContentCreationHub" 
  },
  {
    "hub_id": "tech_analysis_hub",
    "name": "技术分析团队",
    "description": "专注于代码分析、执行和技术问题解决。",
    "capabilities": ["coding", "data_analysis", "debugging"],
    "hub_name": "TechAnalysisHub"
  }
]
```

**2. 任务请求对象 (Task Request Object) - 内存中的结构:**

```python
# 在AEX内部传递的任务对象
task_request = {
    "original_prompt": "请帮我调研一下2025年AI Agent技术的发展趋势，并生成一份总结报告",
    "required_capabilities": ["research", "writing"]
}
```

-----

您可以把这份PRD的内容分块发给Cursor，然后开始指挥它生成代码，例如：

1.  “根据这份PRD，首先为我创建项目的文件结构。”
2.  “现在，根据PRD中的数据结构定义，创建`hubs_config.json`文件。”
3.  “接下来，使用`agno`框架，帮我实现`ContentCreationHub`这个类。它应该包含一个研究员Agent和一个作家Agent。”
4.  “现在为我创建`AgentExchange`这个核心类，并实现加载配置文件的功能。”