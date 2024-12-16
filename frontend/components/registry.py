from typing import Dict, Type, TypeVar, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

T = TypeVar('T')

@dataclass
class ComponentMeta:
    """Metadata for registered components"""
    name: str
    description: str
    category: str = "general"

class ComponentBase(ABC):
    """Base class for all registerable components"""
    @abstractmethod
    def render(self) -> None:
        """Render the component"""
        pass

    @property
    @abstractmethod
    def metadata(self) -> ComponentMeta:
        """Component metadata"""
        pass

class ComponentRegistry:
    """Central registry for UI components"""
    _components: Dict[str, Type[ComponentBase]] = {}
    
    @classmethod
    def register(cls, name: str, description: str, category: str = "general"):
        """Decorator to register a component"""
        def wrapper(component_class: Type[ComponentBase]) -> Type[ComponentBase]:
            component_class.metadata = ComponentMeta(
                name=name,
                description=description,
                category=category
            )
            cls._components[name] = component_class
            return component_class
        return wrapper

    @classmethod
    def get(cls, name: str) -> Optional[Type[ComponentBase]]:
        """Get a registered component by name"""
        return cls._components.get(name)

    @classmethod
    def list_components(cls) -> Dict[str, ComponentMeta]:
        """List all registered components and their metadata"""
        return {name: comp.metadata for name, comp in cls._components.items()}

    @classmethod
    def clear(cls) -> None:
        """Clear all registered components"""
        cls._components.clear()
