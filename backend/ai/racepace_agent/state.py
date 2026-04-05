from pydantic import BaseModel, Field
from backend.ai.racepace_agent.planner.schema import PostgresQuery, QueryResult


class State(BaseModel):
    user_query: str
    is_valid: bool | None = Field(description="Whether the user question is a legitimate F1 question")
    planner_queries: list[PostgresQuery] | None = Field(description="The planner SQL queries")
    query_results: list[QueryResult] | None = Field(default=None, description="Query results from the executor")
