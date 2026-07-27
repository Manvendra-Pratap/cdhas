from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str = Field(..., example="admin", description="SOC Administrator Username")
    password: str = Field(..., example="admin123", description="SOC Administrator Password")

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT Access Token (HMAC-SHA256)")
    refresh_token: str = Field(..., description="JWT Refresh Token")
    token_type: str = Field("bearer", example="bearer", description="Token authentication scheme")
    expires_in: int = Field(3600, example=3600, description="Access token expiration duration in seconds")

class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Valid JWT Refresh Token")

class UserResponse(BaseModel):
    username: str = Field(..., example="admin")
    role: str = Field(..., example="admin")
    status: str = Field("active", example="active")
