import json
import ipfshttpclient
from web3 import Web3
from django.conf import settings
from eth_account import Account
import os
from datetime import datetime

class Web3Service:
    def __init__(self):
        # Connect to Polygon network (you can change to other networks)
        self.w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
        
        # Load contract ABI and address
        with open(os.path.join(settings.BASE_DIR, 'contracts/QuizContract.json')) as f:
            contract_json = json.load(f)
        self.contract = self.w3.eth.contract(
            address=settings.CONTRACT_ADDRESS,
            abi=contract_json['abi']
        )
        
        # Initialize IPFS client
        self.ipfs = ipfshttpclient.connect(settings.IPFS_API_URL)

    def upload_to_ipfs(self, data):
        """Upload data to IPFS and return the hash"""
        json_data = json.dumps(data)
        res = self.ipfs.add_json(json_data)
        return res

    def get_from_ipfs(self, ipfs_hash):
        """Get data from IPFS using its hash"""
        return self.ipfs.get_json(ipfs_hash)

    def register_user(self, user_data, private_key):
        """Register a user on the blockchain"""
        # Upload user data to IPFS
        ipfs_hash = self.upload_to_ipfs(user_data)
        
        # Create transaction
        account = Account.from_key(private_key)
        nonce = self.w3.eth.get_transaction_count(account.address)
        
        # Build transaction
        txn = self.contract.functions.registerUser(ipfs_hash).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 2000000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_txn = self.w3.eth.account.sign_transaction(txn, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for transaction receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def create_quiz(self, quiz_data, private_key):
        """Create a new quiz on the blockchain"""
        # Upload quiz data to IPFS
        ipfs_hash = self.upload_to_ipfs(quiz_data)
        
        # Create transaction
        account = Account.from_key(private_key)
        nonce = self.w3.eth.get_transaction_count(account.address)
        
        # Build transaction
        txn = self.contract.functions.createQuiz(ipfs_hash).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 2000000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_txn = self.w3.eth.account.sign_transaction(txn, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for transaction receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def update_user_progress(self, progress_data, private_key):
        """Update user progress on the blockchain"""
        # Upload progress data to IPFS
        ipfs_hash = self.upload_to_ipfs(progress_data)
        
        # Create transaction
        account = Account.from_key(private_key)
        nonce = self.w3.eth.get_transaction_count(account.address)
        
        # Build transaction
        txn = self.contract.functions.updateUserProgress(ipfs_hash).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 2000000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_txn = self.w3.eth.account.sign_transaction(txn, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for transaction receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def get_quiz(self, quiz_id):
        """Get quiz data from blockchain and IPFS"""
        quiz_data = self.contract.functions.getQuiz(quiz_id).call()
        ipfs_hash = quiz_data[0]
        return {
            'data': self.get_from_ipfs(ipfs_hash),
            'creator': quiz_data[1],
            'is_active': quiz_data[2],
            'created_at': datetime.fromtimestamp(quiz_data[3])
        }

    def get_user_data(self, user_address):
        """Get user data from blockchain and IPFS"""
        user_data = self.contract.functions.getUserData(user_address).call()
        ipfs_hash = user_data[0]
        return {
            'data': self.get_from_ipfs(ipfs_hash),
            'is_registered': user_data[1],
            'last_updated': datetime.fromtimestamp(user_data[2])
        }
