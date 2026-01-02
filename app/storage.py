"""Storage layer abstraction for URL mappings"""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional


class URLStorage(ABC):
    """Abstract base class for URL storage implementations"""
    
    @abstractmethod
    async def save(self, short_id: str, original_url: str) -> None:
        """
        Save a URL mapping.
        
        Args:
            short_id: The short identifier
            original_url: The original URL
        """
        pass
    
    @abstractmethod
    async def get(self, short_id: str) -> Optional[str]:
        """
        Retrieve the original URL for a short ID.
        
        Args:
            short_id: The short identifier to look up
            
        Returns:
            The original URL if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def exists(self, short_id: str) -> bool:
        """
        Check if a short ID exists in storage.
        
        Args:
            short_id: The short identifier to check
            
        Returns:
            True if the ID exists, False otherwise
        """
        pass


class InMemoryURLStorage(URLStorage):
    """
    In-memory implementation of URL storage.
    
    Thread-safe implementation using asyncio locks.
    Suitable for development and testing. For production, consider
    using Redis, PostgreSQL, or other persistent storage.
    """
    
    def __init__(self):
        self._storage: dict[str, str] = {}
        self._lock = asyncio.Lock()
    
    async def save(self, short_id: str, original_url: str) -> None:
        """Save a URL mapping to in-memory storage"""
        async with self._lock:
            self._storage[short_id] = original_url
    
    async def get(self, short_id: str) -> Optional[str]:
        """Retrieve a URL from in-memory storage"""
        async with self._lock:
            return self._storage.get(short_id)
    
    async def exists(self, short_id: str) -> bool:
        """Check if a short ID exists in storage"""
        async with self._lock:
            return short_id in self._storage
