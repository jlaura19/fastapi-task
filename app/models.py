"""Pydantic models for request/response validation"""

from pydantic import BaseModel, Field, field_validator
from app.utils import validate_url


class URLCreateRequest(BaseModel):
    """Request model for creating a shortened URL"""
    
    url: str = Field(
        ...,
        description="The URL to shorten",
        examples=["https://example.com/some/long/path"]
    )
    
    @field_validator('url')
    @classmethod
    def validate_url_format(cls, v: str) -> str:
        """Validate that the URL has a proper format"""
        if not validate_url(v):
            raise ValueError(
                "Invalid URL format. URL must start with http:// or https:// "
                "and contain a valid domain."
            )
        return v


class URLCreateResponse(BaseModel):
    """Response model for successful URL creation"""
    
    short_id: str = Field(
        ...,
        description="The generated short identifier for the URL",
        examples=["abc123"]
    )


class ErrorResponse(BaseModel):
    """Standard error response model"""
    
    detail: str = Field(
        ...,
        description="Error message describing what went wrong"
    )
