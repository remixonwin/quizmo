"""
Base models with functional programming patterns.
"""
from typing import Any, Dict, Optional, TypeVar, List
from django.db import models
from django.utils import timezone
from django.core.cache import cache
from ..utils.functional import immutable, to_dict, memoize

T = TypeVar('T', bound=models.Model)

class TimestampedModel(models.Model):
    """Base model with timestamps."""
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        abstract = True
    
    @property
    def age(self) -> int:
        """Get model age in seconds."""
        if self.created_at:
            return int((timezone.now() - self.created_at).total_seconds())
        return 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return to_dict(self)
    
    @classmethod
    def create_from_dict(cls: type[T], data: Dict[str, Any]) -> T:
        """Create model instance from dictionary."""
        return cls.objects.create(**data)

class SoftDeleteMixin(models.Model):
    """Mixin for soft delete functionality."""
    
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
    
    @property
    def is_deleted(self) -> bool:
        """Check if model is deleted."""
        return bool(self.deleted_at)
    
    def soft_delete(self) -> None:
        """Soft delete model."""
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()
    
    def restore(self) -> None:
        """Restore soft deleted model."""
        self.deleted_at = None
        self.is_active = True
        self.save()
    
    @classmethod
    def active(cls) -> models.QuerySet:
        """Get active model instances."""
        return cls.objects.filter(is_active=True)
    
    @classmethod
    def deleted(cls) -> models.QuerySet:
        """Get deleted model instances."""
        return cls.objects.filter(deleted_at__isnull=False)

class OrderedMixin(models.Model):
    """Mixin for ordering functionality."""
    
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        abstract = True
    
    @classmethod
    def reorder(cls, items: List[T]) -> None:
        """Reorder model instances."""
        for index, item in enumerate(items):
            item.order = index
            item.save()
    
    def move_to(self, new_order: int) -> None:
        """Move model to new position."""
        if new_order != self.order:
            self.order = new_order
            self.save()
    
    def move_up(self) -> None:
        """Move model up one position."""
        if self.order > 0:
            self.move_to(self.order - 1)
    
    def move_down(self) -> None:
        """Move model down one position."""
        self.move_to(self.order + 1)

class CachedMixin(models.Model):
    """Mixin for caching functionality."""
    
    CACHE_TIMEOUT = 60 * 60  # 1 hour
    
    class Meta:
        abstract = True
    
    @classmethod
    def get_cache_key(cls, pk: int) -> str:
        """Get cache key for model instance."""
        return f"{cls.__name__}_{pk}"
    
    @classmethod
    def get_cached(cls, pk: int) -> Optional[T]:
        """Get cached model instance."""
        cache_key = cls.get_cache_key(pk)
        instance = cache.get(cache_key)
        
        if instance is None:
            try:
                instance = cls.objects.get(pk=pk)
                cache.set(cache_key, instance, cls.CACHE_TIMEOUT)
            except cls.DoesNotExist:
                return None
                
        return instance
    
    def invalidate_cache(self) -> None:
        """Invalidate model cache."""
        cache_key = self.get_cache_key(self.pk)
        cache.delete(cache_key)
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save model and invalidate cache."""
        super().save(*args, **kwargs)
        self.invalidate_cache()

class SoftDeleteModel(TimestampedModel, SoftDeleteMixin):
    """Base model with soft delete."""
    class Meta:
        abstract = True

class OrderedModel(TimestampedModel, OrderedMixin):
    """Base model with ordering."""
    class Meta:
        abstract = True
        ordering = ['order']

class CachedModel(TimestampedModel, CachedMixin):
    """Base model with caching."""
    class Meta:
        abstract = True
