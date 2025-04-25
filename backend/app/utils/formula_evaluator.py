from typing import Dict, Any, List
from aeval import Interpreter
from bson import ObjectId

class FormulaEvaluator:
    def __init__(self):
        self.interpreter = Interpreter()
        
    def _create_expression(self, nodes: List[Dict], edges: List[Dict]) -> str:
        """
        Convert nodes and edges into a valid Python expression.
        """
        # Create a mapping of node IDs to their values/operators
        node_map = {}
        for node in nodes:
            node_id = node['id']
            if node['type'] == 'component':
                node_map[node_id] = str(node['data']['value'])
            elif node['type'] == 'constant':
                node_map[node_id] = str(node['data']['value'])
            elif node['type'] == 'operator':
                node_map[node_id] = node['data']['operator']

        # Create expression by following edges
        expression_parts = []
        current_node = None
        
        # Find the starting node (usually a component or constant)
        for node in nodes:
            if not any(edge['target'] == node['id'] for edge in edges):
                current_node = node
                break

        if not current_node:
            raise ValueError("Could not find a starting node")

        # Build expression by following edges
        visited = set()
        stack = [(current_node, False)]
        
        while stack:
            node, is_closing = stack.pop()
            
            if is_closing:
                if node['type'] == 'operator' and node['data']['operator'] == ')':
                    expression_parts.append(')')
                continue
                
            if node['id'] in visited:
                continue
                
            visited.add(node['id'])
            
            if node['type'] == 'operator':
                op = node['data']['operator']
                if op == '(':
                    expression_parts.append('(')
                    # Find matching closing bracket
                    closing_node = next(
                        (n for n in nodes if n['type'] == 'operator' and n['data']['operator'] == ')'),
                        None
                    )
                    if closing_node:
                        stack.append((closing_node, True))
                elif op == 'if':
                    expression_parts.append('lambda x: x if')
                elif op in ['and', 'or', 'not']:
                    expression_parts.append(f' {op} ')
                else:
                    expression_parts.append(f' {op} ')
            else:
                expression_parts.append(node_map[node['id']])
            
            # Add child nodes to stack
            for edge in edges:
                if edge['source'] == node['id']:
                    target_node = next(n for n in nodes if n['id'] == edge['target'])
                    stack.append((target_node, False))

        return ''.join(expression_parts)

    def evaluate(self, nodes: List[Dict], edges: List[Dict], variables: Dict[str, Any] = None) -> float:
        """
        Evaluate the formula represented by nodes and edges.
        
        Args:
            nodes: List of nodes in the formula
            edges: List of edges connecting the nodes
            variables: Dictionary of variable names and their values
            
        Returns:
            The result of the formula evaluation
        """
        try:
            expression = self._create_expression(nodes, edges)
            
            # Set up the evaluation context
            context = variables or {}
            
            # Add any necessary built-in functions
            context.update({
                'abs': abs,
                'min': min,
                'max': max,
                'round': round
            })
            
            # Evaluate the expression
            result = self.interpreter.eval(expression, context)
            
            return float(result)
            
        except Exception as e:
            raise ValueError(f"Error evaluating formula: {str(e)}")

    def validate_formula(self, nodes: List[Dict], edges: List[Dict]) -> bool:
        """
        Validate that the formula is well-formed.
        
        Args:
            nodes: List of nodes in the formula
            edges: List of edges connecting the nodes
            
        Returns:
            True if the formula is valid, False otherwise
        """
        try:
            # Check for basic structural validity
            if not nodes or not edges:
                return False
                
            # Check that all edges reference valid nodes
            node_ids = {node['id'] for node in nodes}
            for edge in edges:
                if edge['source'] not in node_ids or edge['target'] not in node_ids:
                    return False
                    
            # Check for cycles
            visited = set()
            def has_cycle(node_id, path):
                if node_id in path:
                    return True
                if node_id in visited:
                    return False
                    
                visited.add(node_id)
                path.add(node_id)
                
                for edge in edges:
                    if edge['source'] == node_id:
                        if has_cycle(edge['target'], path):
                            return True
                            
                path.remove(node_id)
                return False
                
            for node in nodes:
                if has_cycle(node['id'], set()):
                    return False
                    
            # Try to create and validate the expression
            expression = self._create_expression(nodes, edges)
            self.interpreter.check(expression)
            
            return True
            
        except Exception:
            return False 