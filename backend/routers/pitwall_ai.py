from fastapi import APIRouter, Depends
from langgraph.graph.state import CompiledStateGraph

from backend.ai.pitwall.graph import get_pitwall
from backend.ai.pitwall.schemas import PitWallRequest
from backend.ai.pitwall.state import PitWallChatState

router = APIRouter()


@router.post("/pitwall/call")
async def call_pitwall(request: PitWallRequest, pitwall: CompiledStateGraph = Depends(get_pitwall)):
    state = PitWallChatState(user_query=request.query)
    response = await pitwall.ainvoke(state)

    return response
