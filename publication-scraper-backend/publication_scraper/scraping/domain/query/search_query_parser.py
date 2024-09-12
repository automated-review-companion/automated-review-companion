import ast
from enum import Enum

from scraping.models import SearchEngineType
from utils.logger import Logger

log = Logger(__name__)

class SearchQueryOperator(str, Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

class SearchQueryParser:
    """
    A class to parse search queries.
    Supported operators: AND, OR, NOT
    Supported formats: Semantic Scholar, DBLP, Web of Science

    Attributes:
    expr (str): The search query to parse.
    tree (ast.AST): The abstract syntax tree of the search query
    """

    def __init__(self, expr: str):
        self.expr = expr
        self.tree = ast.parse(expr, mode='eval').body

    def parse(self, format_type) -> str:
        """ 
        Main method to parse the search query. 

        >>> expr = "A and B and C and (D or E and not F)"
        >>> parser = SearchQueryParser(expr)
        >>> parser.parse("SEMANTIC_SCHOLAR")
        "A + B + C + (D | E - F)"
        """
        return self._build_expression(self.tree, format_type)

    
    def _build_expression(self, node: ast.AST, format_type: SearchEngineType) -> str:
        """ 
        Recursively build the search expression. 
        
        Args:
            node (ast.AST): The current node in the AST.
            format_type (str): The format type to generate the search string for.
        """
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return self._format_operator(SearchQueryOperator.AND, node.values, format_type)
            elif isinstance(node.op, ast.Or):
                return self._format_operator(SearchQueryOperator.OR, node.values, format_type)
            
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return self._format_not_operator(self._build_expression(node.operand, format_type), format_type)
        
        elif isinstance(node, ast.Name):
            return self._format_phrase(node.id, format_type)
        
        elif isinstance(node, ast.Constant):  # Handles phrases
            return self._format_phrase(node.value, format_type)
        
        elif isinstance(node, ast.Str):  # Handles string literals (Python < 3.8)
            return self._format_phrase(node.s, format_type)
        
        else:
            raise ValueError("Unsupported expression node")
    

    def _format_operator(self, operator: SearchQueryOperator, operands: list, format_type: SearchEngineType) -> str:
        """ 
        Format the operator and operands based on the format type.
        
        Args:
            operator (str): The operator to format.
            operands (list): The operands to format.
            format_type (str): The format type to generate the search string for.
        """
        formatted_operands = [self._build_expression(op, format_type) for op in operands]
        
        if format_type == SearchEngineType.SEMANTIC_SCHOLAR:
            if operator == SearchQueryOperator.AND:
                joined_operands = " + ".join(formatted_operands)
            elif operator == SearchQueryOperator.OR:
                joined_operands = " | ".join(formatted_operands)

        elif format_type == SearchEngineType.DBLP:
            if operator == SearchQueryOperator.AND:
                joined_operands = " ".join(formatted_operands)
            elif operator == SearchQueryOperator.OR:
                joined_operands = " | ".join(formatted_operands)

        elif format_type == SearchEngineType.WEB_OF_SCIENCE:
            if operator == SearchQueryOperator.AND:
                joined_operands = " ".join(formatted_operands)
            elif operator == SearchQueryOperator.OR:
                joined_operands = " OR ".join(formatted_operands)
        
        # Add parentheses if this is an OR operator to ensure proper precedence
        if operator == SearchQueryOperator.OR:
            return f"({joined_operands})"
        
        return joined_operands
    
    def _format_not_operator(self, operand: str, format_type: SearchEngineType) -> str:
        """ 
        Format the NOT operator based on the format type.
        """
        
        if format_type == SearchEngineType.SEMANTIC_SCHOLAR:
            return f"-{operand}"
        
        elif format_type == SearchEngineType.DBLP:
            return f"-{operand}"  # Assuming no specific NOT syntax, fallback to minus
        
        elif format_type == SearchEngineType.WEB_OF_SCIENCE:
            return f"NOT {operand}"

    def _format_phrase(self, phrase: str, format_type: SearchEngineType) -> str:
        if format_type == SearchEngineType.SEMANTIC_SCHOLAR:
            return f'{phrase}'
        if format_type == SearchEngineType.DBLP:
            return f'{phrase}$'  # Append $ for DBLP
        if format_type == SearchEngineType.WEB_OF_SCIENCE:
            return f'{phrase}'