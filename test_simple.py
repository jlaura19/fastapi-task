"""Simple test script to verify the URL shortening service works"""

import asyncio
from app.storage import InMemoryURLStorage
from app.url_service import URLShortenerService
from app.models import URLCreateRequest


async def main():
    print("Testing URL Shortening Service...")
    print("=" * 50)
    
    # Initialize storage and service
    storage = InMemoryURLStorage()
    service = URLShortenerService(storage)
    
    # Test 1: Create a short URL
    print("\n1. Creating short URL...")
    test_url = "https://example.com/some/long/path"
    short_id = await service.create_short_url(test_url)
    print(f"   ✓ Created short_id: {short_id}")
    
    # Test 2: Retrieve the URL
    print("\n2. Retrieving original URL...")
    retrieved_url = await service.get_original_url(short_id)
    assert retrieved_url == test_url, f"Expected {test_url}, got {retrieved_url}"
    print(f"   ✓ Retrieved: {retrieved_url}")
    
    # Test 3: Test non-existent ID
    print("\n3. Testing non-existent ID...")
    result = await service.get_original_url("nonexistent")
    assert result is None, "Expected None for non-existent ID"
    print("   ✓ Correctly returned None")
    
    # Test 4: Test URL validation
    print("\n4. Testing URL validation...")
    try:
        request = URLCreateRequest(url="https://valid-url.com")
        print("   ✓ Valid URL accepted")
    except Exception as e:
        print(f"   ✗ Valid URL rejected: {e}")
    
    try:
        request = URLCreateRequest(url="not-a-url")
        print("   ✗ Invalid URL accepted (should have failed)")
    except ValueError:
        print("   ✓ Invalid URL correctly rejected")
    
    # Test 5: Test multiple URLs
    print("\n5. Creating multiple URLs...")
    urls = [
        "https://example.com/url1",
        "https://example.com/url2",
        "https://example.com/url3"
    ]
    short_ids = []
    for url in urls:
        sid = await service.create_short_url(url)
        short_ids.append(sid)
    
    assert len(short_ids) == len(set(short_ids)), "Short IDs are not unique!"
    print(f"   ✓ Created {len(short_ids)} unique short IDs")
    
    print("\n" + "=" * 50)
    print("All tests passed! ✓")


if __name__ == "__main__":
    asyncio.run(main())
