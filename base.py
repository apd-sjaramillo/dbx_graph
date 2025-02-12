from typing import Callable, Dict, Any, List
import networkx as nx

class AgentState:
    """Preserves state across tool executions."""
    def __init__(self):
        self.memory: Dict[str, Any] = {}

    def set(self, key: str, value: Any):
        self.memory[key] = value

    def get(self, key: str) -> Any:
        return self.memory.get(key, None)

class ToolRegistry:
    """Manages a collection of tools."""
    def __init__(self):
        self.tools: Dict[str, Callable[[AgentState], Any]] = {}

    def register_tool(self, name: str, func: Callable[[AgentState], Any]):
        self.tools[name] = func

    def get_tool(self, name: str) -> Callable[[AgentState], Any]:
        return self.tools.get(name, None)

class ExecutionGraph:
    """Manages execution dependencies and runs tools dynamically."""
    def __init__(self, state: AgentState):
        self.graph = nx.DiGraph()
        self.state = state
        self.registry = ToolRegistry()

    def add_tool(self, name: str, dependencies: List[str], func: Callable[[AgentState], Any]):
        """Adds a tool to the execution graph with dependencies."""
        self.registry.register_tool(name, func)
        self.graph.add_node(name)
        for dep in dependencies:
            self.graph.add_edge(dep, name)

    def execute(self):
        """Execute tools in order while preserving state."""
        for tool_name in nx.topological_sort(self.graph):
            tool = self.registry.get_tool(tool_name)
            if tool:
                result = tool(self.state)
                self.state.set(tool_name, result)
                print(f"{tool_name} -> {result}")

# Example usage
state = AgentState()
graph = ExecutionGraph(state)

# Define tools
def tool_a(state: AgentState):
    return "Result A"

def tool_b(state: AgentState):
    return f"Result B, depends on A: {state.get('tool_a')}"

def tool_c(state: AgentState):
    return f"Result C, depends on A: {state.get('tool_a')}, B: {state.get('tool_b')}"

# Register tools with dependencies
graph.add_tool("tool_a", [], tool_a)
graph.add_tool("tool_b", ["tool_a"], tool_b)
graph.add_tool("tool_c", ["tool_a", "tool_b"], tool_c)

# Execute the graph
graph.execute()
