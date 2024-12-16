import unittest
from frontend.services.factory import ServiceFactory
from frontend.services.api import APIClient
from frontend.services.auth import AuthService

class TestServiceFactory(unittest.TestCase):
    
    def test_get_api_client_instance(self):
        api_client1 = ServiceFactory.get(APIClient)
        api_client2 = ServiceFactory.get(APIClient)
        self.assertIs(api_client1, api_client2)
    
    def test_get_auth_service_instance(self):
        auth_service1 = ServiceFactory.get(AuthService)
        auth_service2 = ServiceFactory.get(AuthService)
        self.assertIs(auth_service1, auth_service2)
    
    def test_service_factory_clear(self):
        api_client = ServiceFactory.get(APIClient)
        ServiceFactory.clear()
        new_api_client = ServiceFactory.get(APIClient)
        self.assertIsNot(api_client, new_api_client)

if __name__ == '__main__':
    unittest.main()
