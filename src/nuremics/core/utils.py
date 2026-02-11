import ast
import inspect
import textwrap
from typing import Any, Callable, Optional, Type, Union

import attrs
import numpy as np


def convert_value(
    value: object,
) -> Optional[Union[bool, int, float, str, object]]:
    
    if value == "NA":
        return None
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, np.int64)):
        return int(value)
    if isinstance(value, (float, np.float64)):
        return float(value)
    if isinstance(value, str):
        return str(value)
    
    return value


def concat_lists_unique(
    list1: list,
    list2: list,
) -> list:
    
    return list(dict.fromkeys(list1 + list2))


def get_self_method_calls(
    cls: Type,
    method_name: str = "__call__",
) -> list:
    
    method = getattr(cls, method_name, None)
    if method is None:
        return []

    source = inspect.getsource(method)
    source = textwrap.dedent(source)
    tree = ast.parse(source)

    called_methods = []

    class SelfCallVisitor(ast.NodeVisitor):
        def visit_Call(self,
            node: object,
        ) -> list:
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                if node.func.value.id == "self":
                    called_methods.append(node.func.attr)
            self.generic_visit(node)

    SelfCallVisitor().visit(tree)
    return called_methods


# From ChatGPT
def only_function_calls(
    method: Callable[..., Any],
    allowed_methods: list[str],
) -> bool:
    """
    Checks that the method contains only function calls,
    and that all calls are either super().__call__() or self.<allowed_method>().
    """
    
    # Get and dedent source code
    source = inspect.getsource(method)
    source = textwrap.dedent(source)

    # Parse the AST
    tree = ast.parse(source)

    # Expect a FunctionDef node at top level
    func_def = tree.body[0]
    if not isinstance(func_def, ast.FunctionDef):
        return False

    for stmt in func_def.body:
        # Each statement must be a simple expression (Expr) containing a Call
        if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Call):
            return False

        call = stmt.value
        func = call.func

        # Allow super().__call__()
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Call):
            if (
                isinstance(func.value.func, ast.Name)
                and func.value.func.id == 'super'
                and func.attr == '__call__'
            ):
                continue

        # Allow self.<allowed_method>()
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            if func.value.id == 'self' and func.attr in allowed_methods:
                continue

        # If it's neither of the above, reject
        return False

    return True


def extract_inputs_and_types(
    obj: object,
) -> dict:
    
    params = {}
    for field in attrs.fields(obj.__class__):
        if field.metadata.get("input", False):
            params[field.name] = field.type
    
    return params


def extract_analysis(
    obj: object,
) -> list:
    
    analysis = []
    for field in attrs.fields(obj.__class__):
        if field.metadata.get("analysis", False):
            analysis.append(field.name)
    
    return analysis


def extract_outputs(
    obj: object,
) -> list:

    outputs = []
    for field in attrs.fields(obj.__class__):
        if field.metadata.get("output", False):
            outputs.append(field.name)
    
    return outputs
