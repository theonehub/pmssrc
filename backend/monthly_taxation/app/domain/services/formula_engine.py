"""
Formula Engine Domain Service
Safe formula evaluation service for salary component calculations
"""

import ast
import operator
from typing import Dict, Any, List, Optional
from decimal import Decimal
import re

from app.domain.exceptions.salary_component_exceptions import FormulaValidationError


class FormulaEngine:
    """
    Domain service for safe formula evaluation and validation.
    
    Supports mathematical expressions with component references.
    Example: "BASIC * 0.4" for HRA calculation
    """
    
    # Allowed operators for formula evaluation
    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    
    # Allowed functions
    ALLOWED_FUNCTIONS = {
        'min': min,
        'max': max,
        'abs': abs,
        'round': round,
    }
    
    def __init__(self):
        """Initialize formula engine"""
        self.component_pattern = re.compile(r'\b[A-Z][A-Z0-9_]*\b')
    
    def validate_formula(self, formula: str) -> bool:
        """
        Validate that a formula is safe and syntactically correct.
        
        Args:
            formula: The formula to validate
            
        Returns:
            True if valid
            
        Raises:
            FormulaValidationError: If formula is invalid
        """
        if not formula or not formula.strip():
            raise FormulaValidationError(formula, "Formula cannot be empty")
        
        try:
            # Parse the formula into an AST
            tree = ast.parse(formula, mode='eval')
            
            # Validate the AST nodes
            self._validate_ast_node(tree.body)
            
            return True
            
        except SyntaxError as e:
            raise FormulaValidationError(formula, f"Syntax error: {str(e)}")
        except Exception as e:
            raise FormulaValidationError(formula, f"Validation error: {str(e)}")
    
    def extract_component_references(self, formula: str) -> List[str]:
        """
        Extract all component references from a formula.
        
        Args:
            formula: The formula to analyze
            
        Returns:
            List of component codes referenced in the formula
        """
        if not formula:
            return []
        
        # Find all uppercase identifiers (component codes)
        matches = self.component_pattern.findall(formula)
        
        # Filter out Python keywords and functions
        python_keywords = {'AND', 'OR', 'NOT', 'IF', 'ELSE', 'TRUE', 'FALSE'}
        component_refs = [
            match for match in matches 
            if match not in python_keywords and match not in self.ALLOWED_FUNCTIONS
        ]
        
        return list(set(component_refs))  # Remove duplicates
    
    def evaluate_formula(
        self, 
        formula: str, 
        component_values: Dict[str, float]
    ) -> Decimal:
        """
        Safely evaluate a formula with given component values.
        
        Args:
            formula: The formula to evaluate
            component_values: Dictionary of component codes to their values
            
        Returns:
            The calculated result as Decimal
            
        Raises:
            FormulaValidationError: If evaluation fails
        """
        if not formula:
            raise FormulaValidationError(formula, "Formula cannot be empty")
        
        try:
            # Validate formula first
            self.validate_formula(formula)
            
            # Check that all referenced components have values
            referenced_components = self.extract_component_references(formula)
            missing_components = [
                comp for comp in referenced_components 
                if comp not in component_values
            ]
            
            if missing_components:
                raise FormulaValidationError(
                    formula, 
                    f"Missing values for components: {', '.join(missing_components)}"
                )
            
            # Parse and evaluate
            tree = ast.parse(formula, mode='eval')
            result = self._evaluate_ast_node(tree.body, component_values)
            
            # Convert to Decimal for precision
            return Decimal(str(result))
            
        except FormulaValidationError:
            raise
        except Exception as e:
            raise FormulaValidationError(formula, f"Evaluation error: {str(e)}")
    
    def _validate_ast_node(self, node: ast.AST) -> None:
        """
        Recursively validate AST nodes for safety.
        
        Args:
            node: AST node to validate
            
        Raises:
            FormulaValidationError: If node is not allowed
        """
        if isinstance(node, ast.Constant):
            # Allow numbers
            if not isinstance(node.value, (int, float)):
                raise FormulaValidationError("", f"Unsupported constant type: {type(node.value)}")
        
        elif isinstance(node, ast.Name):
            # Allow component references (uppercase identifiers)
            if not node.id.isupper():
                raise FormulaValidationError("", f"Invalid identifier: {node.id}")
        
        elif isinstance(node, ast.BinOp):
            # Allow binary operations
            if type(node.op) not in self.ALLOWED_OPERATORS:
                raise FormulaValidationError("", f"Unsupported operator: {type(node.op)}")
            self._validate_ast_node(node.left)
            self._validate_ast_node(node.right)
        
        elif isinstance(node, ast.UnaryOp):
            # Allow unary operations
            if type(node.op) not in self.ALLOWED_OPERATORS:
                raise FormulaValidationError("", f"Unsupported unary operator: {type(node.op)}")
            self._validate_ast_node(node.operand)
        
        elif isinstance(node, ast.Call):
            # Allow specific functions
            if not isinstance(node.func, ast.Name) or node.func.id not in self.ALLOWED_FUNCTIONS:
                raise FormulaValidationError("", f"Unsupported function: {node.func.id if isinstance(node.func, ast.Name) else 'unknown'}")
            
            # Validate function arguments
            for arg in node.args:
                self._validate_ast_node(arg)
        
        elif isinstance(node, ast.Compare):
            # Allow comparisons (for conditional expressions)
            self._validate_ast_node(node.left)
            for comparator in node.comparators:
                self._validate_ast_node(comparator)
        
        elif isinstance(node, ast.IfExp):
            # Allow conditional expressions
            self._validate_ast_node(node.test)
            self._validate_ast_node(node.body)
            self._validate_ast_node(node.orelse)
        
        else:
            raise FormulaValidationError("", f"Unsupported node type: {type(node)}")
    
    def _evaluate_ast_node(self, node: ast.AST, variables: Dict[str, float]) -> float:
        """
        Recursively evaluate AST nodes.
        
        Args:
            node: AST node to evaluate
            variables: Dictionary of variable values
            
        Returns:
            The evaluated result
        """
        if isinstance(node, ast.Constant):
            return float(node.value)
        
        elif isinstance(node, ast.Name):
            if node.id in variables:
                return float(variables[node.id])
            else:
                raise ValueError(f"Undefined variable: {node.id}")
        
        elif isinstance(node, ast.BinOp):
            left = self._evaluate_ast_node(node.left, variables)
            right = self._evaluate_ast_node(node.right, variables)
            op = self.ALLOWED_OPERATORS[type(node.op)]
            return op(left, right)
        
        elif isinstance(node, ast.UnaryOp):
            operand = self._evaluate_ast_node(node.operand, variables)
            op = self.ALLOWED_OPERATORS[type(node.op)]
            return op(operand)
        
        elif isinstance(node, ast.Call):
            func_name = node.func.id
            func = self.ALLOWED_FUNCTIONS[func_name]
            args = [self._evaluate_ast_node(arg, variables) for arg in node.args]
            return func(*args)
        
        else:
            raise ValueError(f"Unsupported node type in evaluation: {type(node)}")
    
    def get_formula_dependencies(self, formula: str) -> Dict[str, List[str]]:
        """
        Analyze formula dependencies to detect circular references.
        
        Args:
            formula: The formula to analyze
            
        Returns:
            Dictionary mapping component to its dependencies
        """
        dependencies = {}
        if formula:
            referenced_components = self.extract_component_references(formula)
            dependencies[formula] = referenced_components
        
        return dependencies
    
    def detect_circular_dependency(
        self, 
        component_code: str, 
        formula: str, 
        all_formulas: Dict[str, str]
    ) -> Optional[List[str]]:
        """
        Detect if adding this formula would create a circular dependency.
        
        Args:
            component_code: The component being defined
            formula: The formula for the component
            all_formulas: All existing component formulas
            
        Returns:
            List representing the circular path if found, None otherwise
        """
        # Build dependency graph
        dependencies = {}
        for comp_code, comp_formula in all_formulas.items():
            if comp_formula:
                dependencies[comp_code] = self.extract_component_references(comp_formula)
        
        # Add the new formula
        if formula:
            dependencies[component_code] = self.extract_component_references(formula)
        
        # Check for cycles using DFS
        def has_cycle(start: str, current: str, visited: set, path: List[str]) -> Optional[List[str]]:
            if current in visited:
                if current == start:
                    return path + [current]
                return None
            
            visited.add(current)
            path.append(current)
            
            for dependency in dependencies.get(current, []):
                cycle = has_cycle(start, dependency, visited.copy(), path.copy())
                if cycle:
                    return cycle
            
            return None
        
        return has_cycle(component_code, component_code, set(), []) 