from pydantic import BaseModel, Field


class PostgresQuery(BaseModel):
    statement: str


class QueryResult(BaseModel):
    query: PostgresQuery
    result: list[dict]


class PlannerOutput(BaseModel):
    queries: list[PostgresQuery]
    is_valid: bool
