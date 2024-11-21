"""
Web3 service for blockchain interactions.
"""
from web3 import Web3
from django.conf import settings
from eth_account import Account
from django.core.cache import cache
import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class Web3Service:
    """Service for Web3 blockchain interactions."""
    
    def __init__(self):
        """Initialize Web3 connection with contract loading."""
        try:
            # Connect to blockchain network
            self.w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
            
            # Load and cache contract ABI
            self.contract = self._load_contract()
            
        except Exception as e:
            logger.error(f"Failed to initialize Web3Service: {str(e)}")
            raise ConnectionError("Could not initialize Web3 service")
    
    def _load_contract(self):
        """Load contract with caching."""
        cache_key = 'web3_contract'
        contract = cache.get(cache_key)
        
        if not contract:
            try:
                contract_path = os.path.join(settings.BASE_DIR, 'contracts/QuizContract.json')
                with open(contract_path) as f:
                    contract_json = json.load(f)
                
                contract = self.w3.eth.contract(
                    address=settings.CONTRACT_ADDRESS,
                    abi=contract_json['abi']
                )
                
                cache.set(cache_key, contract, timeout=3600)  # Cache for 1 hour
                
            except Exception as e:
                logger.error(f"Failed to load contract: {str(e)}")
                raise
        
        return contract

    def _build_transaction(self, contract_func, account: Account) -> Dict[str, Any]:
        """Build a transaction with proper gas estimation."""
        try:
            nonce = self.w3.eth.get_transaction_count(account.address)
            gas_price = self.w3.eth.gas_price
            
            # Build transaction
            txn = contract_func.build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gasPrice': gas_price
            })
            
            # Estimate gas with buffer
            gas_estimate = int(self.w3.eth.estimate_gas(txn) * 1.2)  # Add 20% buffer
            txn['gas'] = min(gas_estimate, 2000000)  # Cap at 2M gas
            
            return txn
            
        except Exception as e:
            logger.error(f"Failed to build transaction: {str(e)}")
            raise

    def _send_transaction(self, txn: Dict[str, Any], private_key: str) -> Dict[str, Any]:
        """Send and wait for transaction with error handling."""
        try:
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(txn, private_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return tx_receipt
            
        except Exception as e:
            logger.error(f"Failed to send transaction: {str(e)}")
            raise

    def register_user(self, user_data: Dict[str, Any], private_key: str) -> Dict[str, Any]:
        """Register a user on the blockchain."""
        try:
            account = Account.from_key(private_key)
            
            # Build transaction
            register_func = self.contract.functions.registerUser(user_data)
            txn = self._build_transaction(register_func, account)
            
            # Send transaction
            return self._send_transaction(txn, private_key)
            
        except Exception as e:
            logger.error(f"Failed to register user: {str(e)}")
            raise

    def create_quiz(self, quiz_data: Dict[str, Any], private_key: str) -> Dict[str, Any]:
        """Create a new quiz on the blockchain."""
        try:
            account = Account.from_key(private_key)
            
            # Build transaction
            create_func = self.contract.functions.createQuiz(quiz_data)
            txn = self._build_transaction(create_func, account)
            
            # Send transaction
            return self._send_transaction(txn, private_key)
            
        except Exception as e:
            logger.error(f"Failed to create quiz: {str(e)}")
            raise

    def get_quiz(self, quiz_id: int) -> Optional[Dict[str, Any]]:
        """Get quiz data from blockchain."""
        cache_key = f'quiz_data_{quiz_id}'
        quiz_data = cache.get(cache_key)
        
        if not quiz_data:
            try:
                raw_data = self.contract.functions.getQuiz(quiz_id).call()
                
                quiz_data = {
                    'data': raw_data[0],
                    'creator': raw_data[1],
                    'is_active': raw_data[2],
                    'created_at': datetime.fromtimestamp(raw_data[3])
                }
                
                cache.set(cache_key, quiz_data, timeout=300)  # Cache for 5 minutes
                
            except Exception as e:
                logger.error(f"Failed to get quiz {quiz_id}: {str(e)}")
                return None
        
        return quiz_data

    def get_user_data(self, user_address: str) -> Optional[Dict[str, Any]]:
        """Get user data from blockchain."""
        cache_key = f'user_data_{user_address}'
        user_data = cache.get(cache_key)
        
        if not user_data:
            try:
                raw_data = self.contract.functions.getUserData(user_address).call()
                
                user_data = {
                    'data': raw_data[0],
                    'is_registered': raw_data[1],
                    'last_updated': datetime.fromtimestamp(raw_data[2])
                }
                
                cache.set(cache_key, user_data, timeout=300)  # Cache for 5 minutes
                
            except Exception as e:
                logger.error(f"Failed to get user data for {user_address}: {str(e)}")
                return None
        
        return user_data
