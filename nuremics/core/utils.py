import attrs
import ast
import inspect
import textwrap

import numpy as np


def convert_value(value):
    """Function to convert values in python native types"""

    if value == "NA":
        return None
    elif isinstance(value, (bool, np.bool_)):
        return bool(value)
    elif isinstance(value, (int, np.int64)):
        return int(value)
    elif isinstance(value, (float, np.float64)):
        return float(value)
    elif isinstance(value, str):
        return str(value)
    else:
        return value


def concat_lists_unique(
    list1: list,
    list2: list,
):
    return list(dict.fromkeys(list1 + list2))


# From ChatGPT
def get_self_method_calls(cls, method_name="__call__"):
    """Get list of functions called in a specific class"""

    method = getattr(cls, method_name, None)
    if method is None:
        return []

    source = inspect.getsource(method)
    source = textwrap.dedent(source)
    tree = ast.parse(source)

    called_methods = []

    class SelfCallVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                if node.func.value.id == "self":
                    called_methods.append(node.func.attr)
            self.generic_visit(node)

    SelfCallVisitor().visit(tree)
    return called_methods


# From chatGPT
def only_function_calls(method, allowed_methods):
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


# From chatGPT
def extract_inputs_and_types(obj) -> dict:
    params = {}
    for field in attrs.fields(obj.__class__):
        if field.metadata.get("input", False):
            params[field.name] = field.type
    return params


# From chatGPT
def extract_self_output_keys(method):
    """
    Extracts all dictionary keys used in self.output_paths[...] from a method.
    Returns a list of key names as strings.
    """
    keys = []

    # Get and clean source code
    source = inspect.getsource(method)
    source = textwrap.dedent(source)
    tree = ast.parse(source)

    class OutputKeyVisitor(ast.NodeVisitor):
        def visit_Subscript(self, node):
            # Check if it's self.output_paths[...]
            if (isinstance(node.value, ast.Attribute) and
                isinstance(node.value.value, ast.Name) and
                node.value.value.id == "self" and
                node.value.attr == "output_paths"):

                # Extract the key if it's a constant (string)
                if isinstance(node.slice, ast.Constant):
                    keys.append(node.slice.value)
                # Compatibility with Python <3.9: slice is an Index node
                elif isinstance(node.slice, ast.Index) and isinstance(node.slice.value, ast.Constant):
                    keys.append(node.slice.value.value)

            # Continue visiting child nodes
            self.generic_visit(node)

    OutputKeyVisitor().visit(tree)
    return keys