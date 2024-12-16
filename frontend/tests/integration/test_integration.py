import unittest
from unittest.mock import patch
from frontend.services.api import APIClient

class TestIntegrationAPI(unittest.TestCase):
    
    @patch('frontend.services.api.requests.get')
    def test_api_client_get_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"key": "value"}
        
        api = APIClient()
        response = api.get('test-endpoint')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"key": "value"})
    
    @patch('frontend.services.api.requests.post')
    def test_api_client_post_success(self, mock_post):
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": 1}
        
        api = APIClient()
        response = api.post('test-endpoint', data={"name": "test"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"id": 1})

if __name__ == '__main__':
    unittest.main()
