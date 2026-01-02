"""Business logic for URL shortening service"""

from typing import Optional
from app.storage import URLStorage
from app.utils import generate_short_id


class URLShortenerService:
    """
    Service layer for URL shortening operations.
    
    Handles business logic including short ID generation,
    collision detection, and URL retrieval.
    """
    
    def __init__(self, storage: URLStorage, max_retries: int = 5):
        """
        Initialize the URL shortener service.
        
        Args:
            storage: Storage implementation for URL mappings
            max_retries: Maximum attempts to generate a unique short ID
        """
        self.storage = storage
        self.max_retries = max_retries
    
    async def create_short_url(self, original_url: str) -> str:
        """
        Create a shortened URL.
        
        Generates a unique short identifier and stores the mapping.
        Includes collision detection with retry logic.
        
        Args:
            original_url: The URL to shorten
            
        Returns:
            The generated short identifier
            
        Raises:
            RuntimeError: If unable to generate a unique ID after max_retries
        """
        for attempt in range(self.max_retries):
            short_id = generate_short_id(original_url)
            
            # Check for collision
            if not await self.storage.exists(short_id):
                await self.storage.save(short_id, original_url)
                return short_id
        
        # This should be extremely rare with base62 6-character IDs
        raise RuntimeError(
            f"Failed to generate unique short ID after {self.max_retries} attempts"
        )
    
    async def get_original_url(self, short_id: str) -> Optional[str]:
        """
        Retrieve the original URL for a short identifier.
        
        Args:
            short_id: The short identifier to look up
            
        Returns:
            The original URL if found, None otherwise
        """
        return await self.storage.get(short_id)
