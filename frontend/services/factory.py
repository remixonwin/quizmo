from typing import Type, TypeVar, Dict
from frontend.base import BaseService
from functools import lru_cache

T = TypeVar('T', bound=BaseService)

class ServiceFactory:
    """Enhanced service factory with caching"""
    
    _instances: Dict[Type[T], T] = {}
    
    @classmethod
    @lru_cache(maxsize=None)
    def get(cls, service_class: Type[T]) -> T:
        """Get or create cached service instance"""
        if service_class not in cls._instances:
            cls._instances[service_class] = service_class()
        return cls._instances[service_class]

    @classmethod
    def clear(cls) -> None:
        """Clear service cache"""
        cls._instances.clear()
        cls.get.cache_clear()