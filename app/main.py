"""FastAPI URL Shortening Service - Main Application"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.models import URLCreateRequest, URLCreateResponse, ErrorResponse
from app.storage import InMemoryURLStorage
from app.url_service import URLShortenerService

# Initialize FastAPI application
app = FastAPI(
    title="URL Shortening Service",
    description="A simple and efficient URL shortening service built with FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for browser compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage and service
storage = InMemoryURLStorage()
url_service = URLShortenerService(storage)


@app.post(
    "/",
    response_model=URLCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "URL successfully shortened",
            "model": URLCreateResponse
        },
        422: {
            "description": "Invalid URL format",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    },
    summary="Create a shortened URL",
    description="Accepts a URL and returns a shortened identifier"
)
async def create_short_url(request: URLCreateRequest) -> URLCreateResponse:
    """
    Create a shortened URL.
    
    Accepts a valid HTTP/HTTPS URL and returns a unique short identifier.
    The URL must have a valid format with http:// or https:// scheme.
    
    Example:
        Request: {"url": "https://example.com/some/long/path"}
        Response: {"short_id": "abc123"}
    """
    try:
        short_id = await url_service.create_short_url(request.url)
        return URLCreateResponse(short_id=short_id)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@app.get(
    "/{short_id}",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    responses={
        307: {
            "description": "Redirect to original URL",
            "headers": {
                "Location": {
                    "description": "The original URL",
                    "schema": {"type": "string"}
                }
            }
        },
        404: {
            "description": "Short ID not found",
            "model": ErrorResponse
        }
    },
    summary="Redirect to original URL",
    description="Redirects to the original URL associated with the short identifier"
)
async def redirect_to_url(short_id: str) -> RedirectResponse:
    """
    Redirect to the original URL.
    
    Looks up the short identifier and redirects the client to the original URL.
    Returns 404 if the identifier doesn't exist.
    
    Example:
        GET /abc123 -> 307 Redirect to https://example.com/some/long/path
    """
    original_url = await url_service.get_original_url(short_id)
    
    if original_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short ID '{short_id}' not found"
        )
    
    return RedirectResponse(
        url=original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if the service is running"
)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "url-shortener"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
