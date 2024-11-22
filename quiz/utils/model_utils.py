"""
Model utilities for the quiz app.
"""
from typing import Any, Dict, List, Optional, Type, TypeVar
from django.db import models
from django.core.cache import cache
from django.utils import timezone
from functools import wraps

T = TypeVar('T', bound=models.Model)

def cache_model_method(timeout=3600):
    """Cache a model instance method."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            cache_key = f'{self.__class__.__name__}_{self.pk}_{func.__name__}'
            result = cache.get(cache_key)
            if result is None:
                result = func(self, *args, **kwargs)
                cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

def invalidate_model_cache(sender, instance, **kwargs):
    """Invalidate model cache when instance is saved."""
    cache_key = f'{sender.__name__}_{instance.pk}'
    cache.delete_pattern(f'{cache_key}*')

def get_or_none(model: Type[T], **kwargs) -> Optional[T]:
    """Get model instance or None if it doesn't exist."""
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def bulk_update_or_create(
    model: Type[T],
    objects: List[Dict[str, Any]],
    key_fields: List[str],
    batch_size: int = 1000
) -> tuple[List[T], List[T]]:
    """Bulk update or create model instances."""
    existing = {}
    for obj in model.objects.filter(**{
        f'{field}__in': [item[field] for item in objects]
        for field in key_fields
    }):
        key = tuple(getattr(obj, field) for field in key_fields)
        existing[key] = obj

    to_update = []
    to_create = []

    for item in objects:
        key = tuple(item[field] for field in key_fields)
        if key in existing:
            obj = existing[key]
            for field, value in item.items():
                setattr(obj, field, value)
            to_update.append(obj)
        else:
            to_create.append(model(**item))

    created = model.objects.bulk_create(to_create, batch_size=batch_size)
    updated = model.objects.bulk_update(
        to_update,
        [f for f in objects[0].keys() if f not in key_fields],
        batch_size=batch_size
    ) if to_update else []

    return created, updated

class BaseModel(models.Model):
    """Abstract base model with common fields."""
    
    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    """Abstract model that includes timestamp fields."""
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OrderedMixin(models.Model):
    """Mixin for models that need ordering."""
    
    order = models.IntegerField(default=0)

    class Meta:
        abstract = True


class CachedMixin:
    """Mixin for models that need caching."""
    
    @classmethod
    def get_cache_key(cls, identifier):
        """Get cache key for the model instance."""
        return f"{cls.__name__.lower()}_{identifier}"

    def cache_key(self):
        """Get cache key for this instance."""
        return self.get_cache_key(self.pk)

    def invalidate_cache(self):
        """Invalidate cache for this instance."""
        cache.delete(self.cache_key())

class SoftDeleteModel(models.Model):
    """Abstract base class for models with soft delete."""
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """Soft delete the instance."""
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save()
