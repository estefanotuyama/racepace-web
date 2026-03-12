from sqlmodel import Field, SQLModel


class Teams(SQLModel, table=True):
    name: str = Field(primary_key=True)
    color: str
