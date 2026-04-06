from pydantic import BaseModel, Field
from backend.ai.pitwall.planner.schema import PostgresQuery, QueryResult


class PitWallChatState(BaseModel):
    user_query: str
    is_valid: bool | None = Field(default=None, description="Whether the user question is a legitimate F1 question")
    planner_queries: list[PostgresQuery] | None = Field(default=None, description="The planner SQL queries")
    query_results: list[QueryResult] | None = Field(default=None, description="Query results from the executor")
