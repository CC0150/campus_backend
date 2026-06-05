from pydantic import BaseModel, Field, ConfigDict, AliasChoices


class UserLogin(BaseModel):
    student_id: str = Field(validation_alias=AliasChoices("studentId", "username"))
    password: str

    model_config = ConfigDict(populate_by_name=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRegister(BaseModel):
    """注册请求体 — 同时支持驼峰和下划线命名"""
    student_id: str = Field(alias="studentId")
    name: str
    password: str

    model_config = ConfigDict(populate_by_name=True)


class UpdateAddressBody(BaseModel):
    """收货地址同步请求体"""
    addresses: list[str]
    activeAddressIndex: int = 0


class ForgotPasswordCheck(BaseModel):
    """忘记密码 — 步骤1：检查学号是否存在"""
    student_id: str = Field(alias="studentId")

    model_config = ConfigDict(populate_by_name=True)


class ForgotPasswordVerify(BaseModel):
    """忘记密码 — 步骤2：验证密保答案"""
    student_id: str = Field(alias="studentId")
    answer: str

    model_config = ConfigDict(populate_by_name=True)


class ForgotPasswordReset(BaseModel):
    """忘记密码 — 步骤3：重置密码"""
    student_id: str = Field(alias="studentId")
    new_password: str = Field(alias="newPassword")

    model_config = ConfigDict(populate_by_name=True)


class UpdatePasswordBody(BaseModel):
    """修改密码请求体"""
    old_password: str = Field(alias="oldPassword")
    new_password: str = Field(alias="newPassword")

    model_config = ConfigDict(populate_by_name=True)


class TopUpBody(BaseModel):
    """充值请求体"""
    amount: float
