"""
High-level blockchain service combining Web3 and IPFS functionality.
"""
from typing import Dict, Any, Optional
import logging
from .web3_service import Web3Service
from .ipfs_service import IPFSService
from django.core.cache import cache

logger = logging.getLogger(__name__)

class BlockchainService:
    """Service for high-level blockchain operations combining Web3 and IPFS."""
    
    def __init__(self):
        """Initialize Web3 and IPFS services."""
        self.web3 = Web3Service()
        self.ipfs = IPFSService()
    
    def register_user(self, user_data: Dict[str, Any], private_key: str) -> Dict[str, Any]:
        """
        Register a user with data stored on IPFS and reference on blockchain.
        
        Args:
            user_data: User data to store
            private_key: User's private key
            
        Returns:
            Transaction receipt
        """
        try:
            # Upload user data to IPFS
            ipfs_hash = self.ipfs.upload_to_ipfs(user_data)
            
            # Register on blockchain
            tx_receipt = self.web3.register_user(ipfs_hash, private_key)
            
            return tx_receipt
            
        except Exception as e:
            logger.error(f"Failed to register user: {str(e)}")
            raise

    def create_quiz(self, quiz_data: Dict[str, Any], private_key: str) -> Dict[str, Any]:
        """
        Create a new quiz with data stored on IPFS and reference on blockchain.
        
        Args:
            quiz_data: Quiz data to store
            private_key: Creator's private key
            
        Returns:
            Transaction receipt
        """
        try:
            # Upload quiz data to IPFS
            ipfs_hash = self.ipfs.upload_to_ipfs(quiz_data)
            
            # Create on blockchain
            tx_receipt = self.web3.create_quiz(ipfs_hash, private_key)
            
            return tx_receipt
            
        except Exception as e:
            logger.error(f"Failed to create quiz: {str(e)}")
            raise

    def get_quiz(self, quiz_id: int) -> Optional[Dict[str, Any]]:
        """
        Get quiz data from blockchain and IPFS.
        
        Args:
            quiz_id: ID of quiz to retrieve
            
        Returns:
            Quiz data or None if not found
        """
        try:
            # Get blockchain data
            blockchain_data = self.web3.get_quiz(quiz_id)
            if not blockchain_data:
                return None
            
            # Get IPFS data
            ipfs_data = self.ipfs.get_from_ipfs(blockchain_data['data'])
            if not ipfs_data:
                return None
            
            # Combine data
            return {
                **blockchain_data,
                'data': ipfs_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get quiz {quiz_id}: {str(e)}")
            return None

    def get_user_data(self, user_address: str) -> Optional[Dict[str, Any]]:
        """
        Get user data from blockchain and IPFS.
        
        Args:
            user_address: Address of user to retrieve data for
            
        Returns:
            User data or None if not found
        """
        try:
            # Get blockchain data
            blockchain_data = self.web3.get_user_data(user_address)
            if not blockchain_data:
                return None
            
            # Get IPFS data
            ipfs_data = self.ipfs.get_from_ipfs(blockchain_data['data'])
            if not ipfs_data:
                return None
            
            # Combine data
            return {
                **blockchain_data,
                'data': ipfs_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get user data for {user_address}: {str(e)}")
            return None
