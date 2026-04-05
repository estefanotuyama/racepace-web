from backend.ai.racepace_agent.planner.prompt import PLANNER_SYSTEM_PROMPT
from backend.ai.racepace_agent.planner.schema import PostgresQuery, PlannerOutput
from backend.ai.racepace_agent.state import State
from backend.ai.racepace_agent.tools import execute_queries_parallel
from backend.ai.utils import get_deepseek


async def plan_queries(state: State) -> State:
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

async def decide_next_node(state: State) -> str:
    """Caso is_valid = True, continuamos. Caso não, fim."""
    if state.is_valid:
            return "query_executor"
    return "end"


async def paralel_query_executor(state: State):
    queries = state.planner_queries

    result = await execute_queries_parallel(queries)

    return {"query_results": result}