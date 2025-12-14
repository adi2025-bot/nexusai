"""
Code Execution Service
Safe Python code execution sandbox for NexusAI.
"""

import sys
import io
import traceback
import contextlib
import ast
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger("NexusAI.CodeService")


@dataclass
class ExecutionResult:
    """Result of code execution."""
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float = 0.0
    variables: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = {}


# Restricted builtins for safe execution
SAFE_BUILTINS = {
    'abs': abs, 'all': all, 'any': any, 'ascii': ascii,
    'bin': bin, 'bool': bool, 'bytearray': bytearray, 'bytes': bytes,
    'chr': chr, 'complex': complex, 'dict': dict, 'divmod': divmod,
    'enumerate': enumerate, 'filter': filter, 'float': float,
    'format': format, 'frozenset': frozenset, 'hash': hash, 'hex': hex,
    'int': int, 'isinstance': isinstance, 'issubclass': issubclass,
    'iter': iter, 'len': len, 'list': list, 'map': map, 'max': max,
    'min': min, 'next': next, 'oct': oct, 'ord': ord, 'pow': pow,
    'print': print, 'range': range, 'repr': repr, 'reversed': reversed,
    'round': round, 'set': set, 'slice': slice, 'sorted': sorted,
    'str': str, 'sum': sum, 'tuple': tuple, 'type': type, 'zip': zip,
    # Math functions
    'True': True, 'False': False, 'None': None,
}

# Dangerous modules/functions to block
BLOCKED_NAMES = {
    'open', 'file', 'exec', 'eval', 'compile', '__import__',
    'input', 'raw_input', 'exit', 'quit', 'help',
    'globals', 'locals', 'vars', 'dir',
    'getattr', 'setattr', 'delattr', 'hasattr',
    'os', 'sys', 'subprocess', 'shutil', 'pathlib',
    'socket', 'requests', 'urllib', 'http',
    '__builtins__', '__loader__', '__spec__',
}


class CodeValidator:
    """Validate Python code for safety before execution."""
    
    def __init__(self):
        self.violations = []
    
    def validate(self, code: str) -> tuple[bool, list]:
        """
        Validate code for dangerous operations.
        
        Returns:
            (is_safe, list of violations)
        """
        self.violations = []
        
        try:
            tree = ast.parse(code)
            self._check_node(tree)
        except SyntaxError as e:
            self.violations.append(f"Syntax error: {e}")
            return False, self.violations
        
        return len(self.violations) == 0, self.violations
    
    def _check_node(self, node):
        """Recursively check AST nodes for dangerous patterns."""
        for child in ast.walk(node):
            # Check for imports
            if isinstance(child, (ast.Import, ast.ImportFrom)):
                module = getattr(child, 'module', None) or ''
                names = [alias.name for alias in child.names]
                for name in names + [module]:
                    if name.split('.')[0] in BLOCKED_NAMES:
                        self.violations.append(f"Blocked import: {name}")
            
            # Check for dangerous function calls
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id in BLOCKED_NAMES:
                        self.violations.append(f"Blocked function: {child.func.id}")
                elif isinstance(child.func, ast.Attribute):
                    if child.func.attr in BLOCKED_NAMES:
                        self.violations.append(f"Blocked method: {child.func.attr}")
            
            # Check for dangerous names
            if isinstance(child, ast.Name):
                if child.id.startswith('__') and child.id.endswith('__'):
                    if child.id not in ('__name__', '__doc__'):
                        self.violations.append(f"Blocked dunder: {child.id}")


class CodeExecutor:
    """Safe Python code executor with timeout and restrictions."""
    
    def __init__(self, timeout: float = 5.0, max_output_size: int = 10000):
        self.timeout = timeout
        self.max_output_size = max_output_size
        self.validator = CodeValidator()
    
    def execute(self, code: str, context: Dict[str, Any] = None) -> ExecutionResult:
        """
        Execute Python code safely.
        
        Args:
            code: Python code to execute
            context: Optional variables to inject into execution context
        
        Returns:
            ExecutionResult with output, errors, and execution time
        """
        # Validate code first
        is_safe, violations = self.validator.validate(code)
        if not is_safe:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Security violation:\n" + "\n".join(f"• {v}" for v in violations)
            )
        
        # Prepare execution context
        exec_context = context.copy() if context else {}
        exec_context['__builtins__'] = SAFE_BUILTINS
        
        # Add safe standard library modules
        try:
            import math
            import random
            import datetime
            import json
            import re
            import collections
            import itertools
            import functools
            import statistics
            
            exec_context.update({
                'math': math,
                'random': random,
                'datetime': datetime,
                'json': json,
                're': re,
                'collections': collections,
                'itertools': itertools,
                'functools': functools,
                'statistics': statistics,
            })
        except ImportError:
            pass
        
        # Capture output
        output_buffer = io.StringIO()
        start_time = time.time()
        
        try:
            with contextlib.redirect_stdout(output_buffer):
                with contextlib.redirect_stderr(output_buffer):
                    exec(code, exec_context)
            
            execution_time = time.time() - start_time
            output = output_buffer.getvalue()
            
            # Truncate if too long
            if len(output) > self.max_output_size:
                output = output[:self.max_output_size] + "\n... (output truncated)"
            
            # Extract user-defined variables (exclude modules and private)
            user_vars = {
                k: repr(v)[:100] for k, v in exec_context.items()
                if not k.startswith('_') and not callable(v) 
                and k not in SAFE_BUILTINS and k not in ('math', 'random', 'datetime', 'json', 're', 'collections', 'itertools', 'functools', 'statistics')
            }
            
            return ExecutionResult(
                success=True,
                output=output or "(no output)",
                execution_time=execution_time,
                variables=user_vars
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_trace = traceback.format_exc()
            
            return ExecutionResult(
                success=False,
                output=output_buffer.getvalue(),
                error=f"{type(e).__name__}: {str(e)}",
                execution_time=execution_time
            )


def extract_code_blocks(text: str) -> list:
    """Extract Python code blocks from markdown text."""
    import re
    
    # Match ```python ... ``` or ``` ... ```
    pattern = r'```(?:python)?\s*\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    
    return matches


def format_execution_result(result: ExecutionResult) -> str:
    """Format execution result for display."""
    lines = []
    
    if result.success:
        lines.append("✅ **Code executed successfully**")
        lines.append(f"⏱️ Time: {result.execution_time:.3f}s")
        lines.append("")
        lines.append("**Output:**")
        lines.append(f"```\n{result.output}\n```")
        
        if result.variables:
            lines.append("")
            lines.append("**Variables:**")
            for name, value in result.variables.items():
                lines.append(f"- `{name}` = `{value}`")
    else:
        lines.append("❌ **Execution failed**")
        if result.error:
            lines.append(f"```\n{result.error}\n```")
    
    return "\n".join(lines)


# Singleton executor
_executor = None

def get_executor() -> CodeExecutor:
    """Get the code executor singleton."""
    global _executor
    if _executor is None:
        _executor = CodeExecutor()
    return _executor
