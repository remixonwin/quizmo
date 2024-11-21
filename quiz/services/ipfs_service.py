"""
IPFS service for handling decentralized storage.
"""
import json
import ipfshttpclient
from django.conf import settings
from django.core.cache import cache
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class IPFSService:
    """Service for interacting with IPFS."""
    
    def __init__(self):
        """Initialize IPFS client with connection pooling."""
        self._client = None
        self.connect()
    
    def connect(self) -> None:
        """Connect to IPFS with error handling."""
        try:
            if not self._client:
                self._client = ipfshttpclient.connect(settings.IPFS_API_URL)
        except Exception as e:
            logger.error(f"Failed to connect to IPFS: {str(e)}")
            raise ConnectionError("Could not connect to IPFS")

    @property
    def client(self) -> ipfshttpclient.client.Client:
        """Get IPFS client with automatic reconnection."""
        if not self._client:
            self.connect()
        return self._client

    def upload_to_ipfs(self, data: Dict[str, Any]) -> str:
        """
        Upload data to IPFS with caching and error handling.
        
        Args:
            data: Dictionary of data to upload
            
        Returns:
            IPFS hash of uploaded data
        """
        try:
            # Generate cache key from data
            cache_key = f"ipfs_upload_{hash(json.dumps(data, sort_keys=True))}"
            ipfs_hash = cache.get(cache_key)
            
            if not ipfs_hash:
                json_data = json.dumps(data)
                ipfs_hash = self.client.add_json(json_data)
                cache.set(cache_key, ipfs_hash, timeout=3600)  # Cache for 1 hour
            
            return ipfs_hash
            
        except Exception as e:
            logger.error(f"Failed to upload to IPFS: {str(e)}")
            raise

    def get_from_ipfs(self, ipfs_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get data from IPFS with caching and error handling.
        
        Args:
            ipfs_hash: IPFS hash to retrieve
            
        Returns:
            Retrieved data or None if not found
        """
        try:
            # Check cache first
            cache_key = f"ipfs_data_{ipfs_hash}"
            data = cache.get(cache_key)
            
            if not data:
                data = self.client.get_json(ipfs_hash)
                if data:
                    cache.set(cache_key, data, timeout=3600)  # Cache for 1 hour
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get data from IPFS: {str(e)}")
            return None

    def __del__(self):
        """Cleanup IPFS client connection."""
        try:
            if self._client:
                self._client.close()
        except:
            pass  # Ignore cleanup errors
