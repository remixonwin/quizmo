import unittest
from unittest.mock import patch, Mock
from frontend.services.api import APIClient
import requests

class TestAPIClientIntegration(unittest.TestCase):
    def setUp(self):
        self.api = APIClient()
        self.test_endpoint = 'test/endpoint'
        self.test_data = {'key': 'value'}
        self.test_headers = {'Authorization': 'Token xyz'}

    @patch('frontend.services.api.requests.get')
    def test_get_request_success(self, mock_get):
        mock_get.return_value = Mock(status_code=200, json=lambda: self.test_data)
        response = self.api.get(self.test_endpoint, headers=self.test_headers)
        
        mock_get.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.test_data)

    @patch('frontend.services.api.requests.post')
    def test_post_request_success(self, mock_post):
        mock_post.return_value = Mock(status_code=201, json=lambda: self.test_data)
        response = self.api.post(
            self.test_endpoint, 
            data=self.test_data, 
            headers=self.test_headers
        )
        
        mock_post.assert_called_once()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), self.test_data)

    @patch('frontend.services.api.requests.delete')
    def test_delete_request_success(self, mock_delete):
        mock_delete.return_value = Mock(status_code=204)
        response = self.api.delete(self.test_endpoint, headers=self.test_headers)
        
        mock_delete.assert_called_once()
        self.assertEqual(response.status_code, 204)

    def test_connection_error_handling(self):
        with patch('frontend.services.api.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError()
            with patch('frontend.services.api.st') as mock_st:
                response = self.api.get(self.test_endpoint)
                self.assertIsNone(response)
                mock_st.error.assert_called_once()

    def test_timeout_error_handling(self):
        with patch('frontend.services.api.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()
            with patch('frontend.services.api.st') as mock_st:
                response = self.api.get(self.test_endpoint)
                self.assertIsNone(response)
                mock_st.error.assert_called_once()

if __name__ == '__main__':
    unittest.main()
