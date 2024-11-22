"""
Service for handling user data storage using Django's cache system.
"""
from django.core.cache import cache

class BlockchainService:
    """
    Service class that handles user data storage using Django's cache system.
    This is a simplified version that replaces the previous blockchain/IPFS implementation.
    """
    
    @staticmethod
    def store_user_data(user_id: str, data: dict) -> bool:
        """
        Store user data in Django's cache.
        
        Args:
            user_id (str): Unique identifier for the user
            data (dict): User data to store
            
        Returns:
            bool: True if storage was successful, False otherwise
        """
        try:
            cache_key = f"user_data_{user_id}"
            cache.set(cache_key, data, timeout=None)  # No timeout, data persists until explicitly deleted
            return True
        except Exception as e:
            print(f"Error storing user data: {str(e)}")
            return False

    @staticmethod
    def get_user_data(user_id: str) -> dict:
        """
        Retrieve user data from Django's cache.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            dict: User data if found, empty dict if not found
        """
        try:
            cache_key = f"user_data_{user_id}"
            data = cache.get(cache_key)
            return data if data else {}
        except Exception as e:
            print(f"Error retrieving user data: {str(e)}")
            return {}
