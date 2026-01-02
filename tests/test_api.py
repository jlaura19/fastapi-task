"""Comprehensive test suite for URL shortening API"""

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from app.main import app as main_app
from app.storage import InMemoryURLStorage
from app.url_service import URLShortenerService


@pytest.fixture
def app():
    """Create a fresh app instance for each test"""
    # Create new storage for test isolation
    storage = InMemoryURLStorage()
    service = URLShortenerService(storage)
    
    # Override the app's service with our test instance
    main_app.state.storage = storage
    main_app.state.service = service
    
    # Update the dependency
    from app import main
    main.storage = storage
    main.url_service = service
    
    return main_app


@pytest.mark.asyncio
async def test_create_short_url_success(app):
    """Test successful URL creation returns 201 with short_id"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/",
            json={"url": "https://example.com/some/long/path"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "short_id" in data
        assert isinstance(data["short_id"], str)
        assert len(data["short_id"]) > 0


@pytest.mark.asyncio
async def test_redirect_to_original_url(app):
    """Test that redirect returns 307 with correct Location header"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False
    ) as client:
        # First, create a short URL
        create_response = await client.post(
            "/",
            json={"url": "https://example.com/test"}
        )
        short_id = create_response.json()["short_id"]
        
        # Then, test the redirect
        redirect_response = await client.get(f"/{short_id}")
        
        assert redirect_response.status_code == 307
        assert redirect_response.headers["location"] == "https://example.com/test"


@pytest.mark.asyncio
async def test_nonexistent_short_id_returns_404(app):
    """Test that non-existent short_id returns 404"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False
    ) as client:
        response = await client.get("/nonexistent123")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_invalid_url_format_returns_422(app):
    """Test that invalid URL format returns 422 validation error"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Test various invalid URL formats
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "javascript:alert('xss')",
            "",
            "example.com",  # Missing scheme
        ]
        
        for invalid_url in invalid_urls:
            response = await client.post(
                "/",
                json={"url": invalid_url}
            )
            assert response.status_code == 422, f"Failed for URL: {invalid_url}"


@pytest.mark.asyncio
async def test_duplicate_url_handling(app):
    """Test that submitting the same URL multiple times works correctly"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        url = "https://example.com/duplicate-test"
        
        # Create first short URL
        response1 = await client.post("/", json={"url": url})
        assert response1.status_code == 201
        short_id1 = response1.json()["short_id"]
        
        # Create second short URL for same URL
        response2 = await client.post("/", json={"url": url})
        assert response2.status_code == 201
        short_id2 = response2.json()["short_id"]
        
        # Both should work (may or may not be the same ID)
        assert isinstance(short_id1, str)
        assert isinstance(short_id2, str)


@pytest.mark.asyncio
async def test_concurrent_requests(app):
    """Test that concurrent requests are handled correctly"""
    import asyncio
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Create multiple URLs concurrently
        urls = [f"https://example.com/concurrent/{i}" for i in range(10)]
        
        tasks = [
            client.post("/", json={"url": url})
            for url in urls
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 201
            assert "short_id" in response.json()
        
        # All short_ids should be unique
        short_ids = [r.json()["short_id"] for r in responses]
        assert len(short_ids) == len(set(short_ids))


@pytest.mark.asyncio
async def test_health_check(app):
    """Test health check endpoint"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_various_valid_urls(app):
    """Test that various valid URL formats are accepted"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        valid_urls = [
            "https://example.com",
            "http://example.com/path",
            "https://subdomain.example.com/path?query=value",
            "https://example.com:8080/path",
            "https://example.com/path#fragment",
            "https://example.com/path?a=1&b=2",
        ]
        
        for valid_url in valid_urls:
            response = await client.post("/", json={"url": valid_url})
            assert response.status_code == 201, f"Failed for URL: {valid_url}"
            assert "short_id" in response.json()

