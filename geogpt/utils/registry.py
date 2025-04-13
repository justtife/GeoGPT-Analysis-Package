from typing import Dict, List, Callable, Optional
from dataclasses import dataclass

@dataclass
class FunctionMetadata:
    """Stores metadata for registered functions"""
    name: str
    description: str
    func: Callable
    inputs: List[str]
    outputs: List[str]
    tags: List[str]


class FunctionRegistry:
    """Simplified but professional function registry"""

    def __init__(self):
        self._registry: Dict[str, FunctionMetadata] = {}

    def register(self, func: Callable, name: str, description: str,
                 inputs: List[str], outputs: List[str], tags: List[str]) -> None:
        """Register a function with metadata"""
        self._registry[name] = FunctionMetadata(
            name=name,
            description=description,
            func=func,
            inputs=inputs,
            outputs=outputs,
            tags=tags
        )

    def get_function(self, name: str) -> Optional[FunctionMetadata]:
        """Get function by name"""
        return self._registry.get(name)

    def get_all_functions(self) -> Dict[str, FunctionMetadata]:
        """Get all registered functions"""
        return self._registry

    def get_functions_by_tag(self, tag: str) -> List[FunctionMetadata]:
        """Get functions matching a tag"""
        return [meta for meta in self._registry.values() if tag in meta.tags]


# Global registry instance
global_registry = FunctionRegistry()


def register_function(name: str, description: str,
                      inputs: List[str], outputs: List[str],
                      tags: List[str]) -> Callable:
    """Decorator to register functions"""
    def decorator(func: Callable) -> Callable:
        global_registry.register(
            func, name, description, inputs, outputs, tags)
        return func
    return decorator
