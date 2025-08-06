from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json

class BaseTool(ABC):
    """Base class for all tools in the chat application"""
    
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace('tool', '')
        self.description = self.get_description()
    
    @abstractmethod
    def get_description(self) -> str:
        """Return the description of what this tool does"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with the given parameters"""
        pass
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate the input parameters"""
        try:
            # Basic validation - can be overridden by subclasses
            required_params = self.get_required_parameters()
            for param in required_params:
                if param not in kwargs:
                    raise ValueError(f"Missing required parameter: {param}")
            return True
        except Exception as e:
            raise ValueError(f"Parameter validation failed: {str(e)}")
    
    def get_required_parameters(self) -> list:
        """Get list of required parameters - can be overridden by subclasses"""
        # Default implementation - subclasses can override
        return [] 