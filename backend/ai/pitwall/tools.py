import asyncio

from sqlalchemy import text
from sqlmodel import Session

from backend.ai.pitwall.planner.schema import PostgresQuery, QueryResult
from backend.db.database import engine


def _run_query(query: PostgresQuery) -> QueryResult:
    with Session(engine) as session:
        result = session.execute(text(query.statement))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        return QueryResult(query=query, result=rows)


async def execute_queries_parallel(queries: list[PostgresQuery]) -> list[QueryResult]:
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(None, _run_query, q) for q in queries]
    return list(await asyncio.gather(*tasks))