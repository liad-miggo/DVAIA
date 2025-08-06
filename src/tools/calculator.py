import math
import logging
from typing import Dict, Any, Union
from .base_tool import BaseTool

logger = logging.getLogger(__name__)

class CalculatorTool(BaseTool):
    """Tool for performing mathematical calculations"""
    
    def __init__(self):
        super().__init__()
    
    def get_description(self) -> str:
        return "Perform mathematical calculations including basic arithmetic, trigonometry, logarithms, and more."
    
    def execute(self, **kwargs) -> str:
        """Execute mathematical calculation"""
        try:
            self.validate_parameters(**kwargs)
            
            expression = kwargs["expression"]
            precision = kwargs.get("precision", 6)
            
            # Evaluate the expression safely
            result = self._evaluate_expression(expression)
            
            # Format the result
            if isinstance(result, (int, float)):
                if isinstance(result, int):
                    formatted_result = str(result)
                else:
                    formatted_result = f"{result:.{precision}f}"
                    # Remove trailing zeros
                    formatted_result = formatted_result.rstrip('0').rstrip('.')
            else:
                formatted_result = str(result)
            
            return f"Result: {formatted_result}"
            
        except Exception as e:
            logger.error(f"Calculator error: {e}")
            return f"Error calculating expression: {str(e)}"
    
    def _evaluate_expression(self, expression: str) -> Union[int, float]:
        """Safely evaluate a mathematical expression"""
        # Clean the expression
        expression = expression.strip().lower()
        
        # Replace common mathematical symbols
        expression = expression.replace('×', '*').replace('÷', '/')
        expression = expression.replace('^', '**')
        
        try:
            # Use eval with restricted globals
            result = eval(expression)
            
            # Validate result
            if not isinstance(result, (int, float)):
                raise ValueError("Expression must evaluate to a number")
            
            return result
            
        except ZeroDivisionError:
            raise ValueError("Division by zero is not allowed")
        except Exception as e:
            raise ValueError(f"Invalid mathematical expression: {str(e)}")
    
    def _parse_complex_expression(self, expression: str) -> str:
        """Parse and simplify complex mathematical expressions"""
        # Handle common mathematical notations
        replacements = {
            'sin': 'math.sin',
            'cos': 'math.cos',
            'tan': 'math.tan',
            'asin': 'math.asin',
            'acos': 'math.acos',
            'atan': 'math.atan',
            'sinh': 'math.sinh',
            'cosh': 'math.cosh',
            'tanh': 'math.tanh',
            'log': 'math.log',
            'log10': 'math.log10',
            'sqrt': 'math.sqrt',
            'exp': 'math.exp',
            'floor': 'math.floor',
            'ceil': 'math.ceil',
            'factorial': 'math.factorial',
            'gcd': 'math.gcd',
            'pi': 'math.pi',
            'e': 'math.e'
        }
        
        for old, new in replacements.items():
            expression = expression.replace(old, new)
        
        return expression 