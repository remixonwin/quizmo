"""
Functional programming utilities for the quiz application.

This module provides pure functions and functional programming constructs
to support immutable data handling and function composition.
"""
from typing import TypeVar, Callable, Iterable, Any, List, Dict, Optional, Union, Generic
from functools import reduce, partial, wraps
from itertools import groupby
from datetime import datetime
from django.utils import timezone
from django.core.cache import cache
from django.http import HttpRequest
from django.db.models import QuerySet, Model

T = TypeVar('T')
R = TypeVar('R')

def compose(*functions: Callable) -> Callable:
    """
    Compose multiple functions from right to left.
    
    Args:
        *functions: Functions to compose
        
    Returns:
        Composed function
    """
    return reduce(lambda f, g: lambda x: f(g(x)), functions)

def pipe(*functions: Callable) -> Callable:
    """
    Compose multiple functions from left to right.
    
    Args:
        *functions: Functions to pipe
        
    Returns:
        Piped function
    """
    return compose(*reversed(functions))

def memoize(func: Callable) -> Callable:
    """
    Memoize function results using Django's cache.
    
    Args:
        func: Function to memoize
        
    Returns:
        Memoized function with cache_clear method
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key specific to the function and its arguments
        key = f"memo_{func.__name__}_{str(args)}_{str(kwargs)}"
        result = cache.get(key)
        if result is None or getattr(wrapper, '_clear_next_call', False):
            result = func(*args, **kwargs)
            cache.set(key, result)
            wrapper._clear_next_call = False
        return result
    
    def cache_clear():
        """Clear cached result for this function instance."""
        # Since we can't easily clear all keys for this function,
        # we'll just invalidate the cache for the current instance
        wrapper._clear_next_call = True
    
    # Add cache clearing capability
    wrapper._clear_next_call = False
    wrapper.cache_clear = cache_clear
    return wrapper

def safe_get(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary values.
    
    Args:
        data: Dictionary to traverse
        *keys: Keys to follow
        default: Default value if path not found
        
    Returns:
        Value at path or default
    """
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError, IndexError):
            return default
    return data

def filter_none(items: Iterable[Optional[T]]) -> List[T]:
    """
    Filter out None values from iterable.
    
    Args:
        items: Iterable potentially containing None
        
    Returns:
        List with None values removed
    """
    return [item for item in items if item is not None]

def group_by(key: Callable[[T], Any], items: Iterable[T]) -> Dict[Any, List[T]]:
    """
    Group items by key function.
    
    Args:
        key: Function to generate grouping key
        items: Items to group
        
    Returns:
        Dictionary of grouped items
    """
    sorted_items = sorted(items, key=key)
    return {k: list(g) for k, g in groupby(sorted_items, key=key)}

def to_dict(model_instance: Model) -> Dict[str, Any]:
    """
    Convert Django model instance to dictionary.
    
    Args:
        model_instance: Django model instance
        
    Returns:
        Dictionary representation
    """
    return {
        field.name: getattr(model_instance, field.name)
        for field in model_instance._meta.fields
    }

def immutable(cls: type) -> type:
    """
    Class decorator to make instances immutable.
    
    Args:
        cls: Class to make immutable
        
    Returns:
        Immutable class
    """
    def __setattr__(self, *args, **kwargs):
        raise TypeError(f"Cannot modify {cls.__name__} instance")
    
    cls.__setattr__ = __setattr__
    return cls

def curry(func: Callable) -> Callable:
    """
    Curry a function for partial application.
    
    Args:
        func: Function to curry
        
    Returns:
        Curried function
    """
    @wraps(func)
    def curried(*args, **kwargs):
        if len(args) + len(kwargs) >= func.__code__.co_argcount:
            return func(*args, **kwargs)
        return partial(curried, *args, **kwargs)
    return curried

def map_queryset(func: Callable[[Model], R], queryset: QuerySet) -> List[R]:
    """
    Map function over queryset efficiently.
    
    Args:
        func: Mapping function
        queryset: Django queryset
        
    Returns:
        List of mapped values
    """
    return [func(obj) for obj in queryset.iterator()]

def map_values(func: Callable[[T], R], dictionary: Dict[Any, T]) -> Dict[Any, R]:
    """
    Map function over dictionary values.
    
    Args:
        func: Function to apply to values
        dictionary: Dictionary to transform
        
    Returns:
        Dictionary with transformed values
    """
    return {k: func(v) for k, v in dictionary.items()}

def validate_request(
    validators: List[Callable[[HttpRequest], bool]]
) -> Callable:
    """
    Compose request validators.
    
    Args:
        validators: List of validator functions
        
    Returns:
        Combined validator function
    """
    def validate(request: HttpRequest) -> bool:
        return all(validator(request) for validator in validators)
    return validate

def time_window(
    start: datetime,
    end: datetime,
    func: Callable[[datetime, datetime], R]
) -> R:
    """
    Execute function within time window.
    
    Args:
        start: Start time
        end: End time
        func: Function to execute
        
    Returns:
        Function result
    """
    current = timezone.now()
    if start <= current <= end:
        return func(start, end)
    return None

class Maybe(Generic[T]):
    """
    Maybe monad for handling optional values.
    """
    def __init__(self, value: Optional[T] = None):
        self._value = value

    @property
    def value(self) -> Optional[T]:
        return self._value

    def is_some(self) -> bool:
        return self._value is not None

    def is_none(self) -> bool:
        return self._value is None

    def map(self, func: Callable[[T], R]) -> 'Maybe[R]':
        if self.is_none():
            return Maybe(None)
        return Maybe(func(self._value))

    def bind(self, func: Callable[[T], 'Maybe[R]']) -> 'Maybe[R]':
        if self.is_none():
            return Maybe(None)
        return func(self._value)

    def get_or_else(self, default: T) -> T:
        return self._value if self.is_some() else default

def maybe(value: Optional[T]) -> Maybe[T]:
    """
    Create a Maybe monad instance.
    
    Args:
        value: Value to wrap in Maybe
        
    Returns:
        Maybe monad instance
    """
    return Maybe(value)

class Either(Generic[T]):
    """
    Either monad for handling computations that may fail.
    """
    def __init__(self, left: Optional[Any] = None, right: Optional[T] = None):
        self._left = left
        self._right = right

    @property
    def value(self) -> Union[Any, T]:
        return self._right if self.is_right() else self._left

    def is_left(self) -> bool:
        return self._left is not None

    def is_right(self) -> bool:
        return self._right is not None

    def map(self, func: Callable[[T], R]) -> 'Either[R]':
        if self.is_left():
            return Either(left=self._left)
        return Either(right=func(self._right))

    def bind(self, func: Callable[[T], 'Either[R]']) -> 'Either[R]':
        if self.is_left():
            return Either(left=self._left)
        return func(self._right)

def either(value: Union[Exception, T]) -> Either[T]:
    """
    Create an Either monad instance.
    
    Args:
        value: Value or exception to wrap in Either
        
    Returns:
        Either monad instance
    """
    if isinstance(value, Exception):
        return Either(left=value)
    return Either(right=value)

def fmap(func: Callable[[T], R], container: Union[Maybe[T], Either[T]]) -> Union[Maybe[R], Either[R]]:
    """
    Map a function over a monadic container.
    
    Args:
        func: Function to apply
        container: Monadic container (Maybe or Either)
        
    Returns:
        New container with mapped value
    """
    return container.map(func)

def bind(container: Union[Maybe[T], Either[T]], func: Callable[[T], Union[Maybe[R], Either[R]]]) -> Union[Maybe[R], Either[R]]:
    """
    Bind a monadic function to a container.
    
    Args:
        container: Monadic container (Maybe or Either)
        func: Monadic function to apply
        
    Returns:
        New container from function application
    """
    return container.bind(func)
