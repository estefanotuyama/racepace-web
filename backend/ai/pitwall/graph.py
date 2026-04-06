from langgraph.constants import START, END
from langgraph.graph import StateGraph

from backend.ai.pitwall.planner.node import plan_queries, decide_next_node, paralel_query_executor
from backend.ai.pitwall.state import PitWallChatState

graph_builder = StateGraph(PitWallChatState)

# NODES
graph_builder.add_node("plan_queries", plan_queries)
graph_builder.add_node("query_executor", paralel_query_executor)

# EDGES
graph_builder.add_edge(START, "plan_queries")

graph_builder.add_conditional_edges(
    "plan_queries",
    decide_next_node,
    {
    "query_executor": "query_executor",
    "end": END
    }
)
graph_builder.add_edge("query_executor", END)

pitwall_graph = graph_builder.compile()

def get_pitwall():
    return pitwall_graph