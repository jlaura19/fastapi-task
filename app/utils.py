"""Utility functions for URL shortening service"""

import hashlib
import secrets
import string
from urllib.parse import urlparse


def generate_short_id(url: str, length: int = 6) -> str:
    """
    Generate a short, URL-safe identifier for a given URL.
    
    Uses a combination of hashing and random data to create collision-resistant IDs.
    The ID uses base62 encoding (a-zA-Z0-9) for maximum URL compatibility.
    
    Args:
        url: The original URL to generate an ID for
        length: Length of the generated ID (default: 6 characters)
        
    Returns:
        A URL-safe short identifier
    """
    # Combine URL hash with random data for collision resistance
    hash_input = f"{url}{secrets.token_hex(8)}".encode('utf-8')
    hash_digest = hashlib.sha256(hash_input).hexdigest()
    
    # Convert to base62 (alphanumeric only)
    base62_chars = string.ascii_letters + string.digits
    
    # Use hash to seed the ID generation
    result = []
    hash_int = int(hash_digest[:16], 16)  # Use first 16 hex chars
    
    for _ in range(length):
        hash_int, remainder = divmod(hash_int, 62)
        result.append(base62_chars[remainder])
    
    return ''.join(result)


def validate_url(url: str) -> bool:
    """
    Validate that a URL has a proper format.
    
    Checks for:
    - Valid scheme (http or https)
    - Valid network location (domain)
    
    Args:
        url: The URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        return all([
            parsed.scheme in ('http', 'https'),
            parsed.netloc,
            len(url) > 0
        ])
    except Exception:
        return False
