from pydantic import BaseModel, Field


# DTO
class PitWallRequest(BaseModel):
    query: str = Field(description="The user question", min_length=1, max_length=1000)