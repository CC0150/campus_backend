from pydantic import BaseModel, Field, ConfigDict


class UserResponse(BaseModel):
    student_id: str = Field(serialization_alias="studentId")
    name: str
    balance: float
    avatar: str
    addresses: list[str] = []
    active_address_index: int = Field(default=0, serialization_alias="activeAddressIndex")
    security_question: str = Field(default="你的第一只宠物叫什么名字？", serialization_alias="securityQuestion")
    security_answer: str = Field(default="小白", serialization_alias="securityAnswer")

    model_config = ConfigDict(from_attributes=True)
