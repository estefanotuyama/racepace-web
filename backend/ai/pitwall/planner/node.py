from backend.ai.pitwall.planner.prompt import PLANNER_SYSTEM_PROMPT
from backend.ai.pitwall.planner.schema import PostgresQuery, PlannerOutput
from backend.ai.pitwall.state import PitWallChatState
from backend.ai.pitwall.tools import execute_queries_parallel
from backend.ai.utils import get_deepseek


async def plan_queries(state: PitWallChatState) -> PitWallChatState:
    user_query = state.user_query

    llm = get_deepseek().with_structured_output(PlannerOutput)

    msgs = [
        ("system", PLANNER_SYSTEM_PROMPT),
        ("user", user_query)
    ]

    response = await llm.ainvoke(msgs)

    return {
        "is_valid": response.is_valid,
        "planner_queries": response.queries,
    }

async def decide_next_node(state: PitWallChatState) -> str:
    """Caso is_valid = True, continuamos. Caso não, fim."""
    if state.is_valid:
            return "query_executor"
    return "end"


async def paralel_query_executor(state: PitWallChatState):
    queries = state.planner_queries

    result = await execute_queries_parallel(queries)

    return {"query_results": result}