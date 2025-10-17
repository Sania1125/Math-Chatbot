
import ast
import operator
import math
import re
import sys
import json

def safe_eval(expr):
    # Preprocess to support percentage literals like '50%' -> '0.5'
    def _replace_percentages(s: str) -> str:
        # replace numbers followed by % with their decimal equivalents
        def repl(m):
            num = float(m.group(1))
            return str(num / 100.0)
        return re.sub(r"(\d+(?:\.\d+)?)%", repl, s)

    expr = _replace_percentages(expr)
    # Convert degree literals like '60°' to radians using numeric pi
    expr = re.sub(r"(\d+(?:\.\d+)?)\s*°", lambda m: f"({m.group(1)} * {math.pi} / 180)", expr)
    # Allow shorthand trig forms like 'sin60' or 'cos 45' -> convert to radians
    expr = re.sub(r"\b(sin|cos|tan)\s*\(?\s*(-?\d+(?:\.\d+)?)\s*\)?",
                  lambda m: f"{m.group(1)}({m.group(2)} * pi / 180)",
                  expr,
                  flags=re.IGNORECASE)

    # convert trig calls with inner numeric expressions like sin(30+15) to degrees -> radians
    # only convert when the inner expression contains digits/operators (no letters/functions)
    expr = re.sub(r"\b(sin|cos|tan)\s*\(\s*([0-9\.\s\+\-\*\/\(\)]+)\s*\)",
                  lambda m: f"{m.group(1)}(({m.group(2)}) * pi / 180)",
                  expr,
                  flags=re.IGNORECASE)
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg
    }

    allowed_functions = {
        # basic
        'sqrt': math.sqrt,
        'pow': math.pow,
    'radians': math.radians,
        # trig/log/exp
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'ln': math.log,
        'exp': math.exp,
        'abs': abs,
        'floor': math.floor,
        'ceil': math.ceil,
        # statistics (implemented below)
        'mean': None,
        'avg': None,
        'median': None
    }

    # named constants available in expressions (pi, e)
    allowed_names = {
        'pi': math.pi,
        'e': math.e
    }

    # implement mean/avg/median using local helpers
    def _mean(values):
        if not values:
            raise ValueError("mean()/avg() requires at least one value")
        return sum(values) / len(values)

    def _median(values):
        if not values:
            raise ValueError("median() requires at least one value")
        s = sorted(values)
        n = len(s)
        mid = n // 2
        if n % 2 == 1:
            return s[mid]
        else:
            return (s[mid - 1] + s[mid]) / 2.0

    allowed_functions['mean'] = _mean
    allowed_functions['avg'] = _mean
    allowed_functions['median'] = _median

    def eval_node(node):
        # numbers (modern AST uses Constant)
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            else:
                raise ValueError("Invalid constant")
        elif isinstance(node, ast.Name):
            if node.id in allowed_names:
                return allowed_names[node.id]
            else:
                raise ValueError(f"Unsupported name: {node.id}")
        elif isinstance(node, ast.List) or isinstance(node, ast.Tuple):
            return [eval_node(elt) for elt in node.elts]
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in allowed_operators:
                right = eval_node(node.right)
                if op_type is ast.Div and right == 0:
                    return "Error: Division by zero is not allowed."
                return allowed_operators[op_type](eval_node(node.left), right)
            else:
                raise ValueError("Unsupported operator")
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in allowed_operators:
                return allowed_operators[op_type](eval_node(node.operand))
            else:
                raise ValueError("Unsupported unary operator")
        elif isinstance(node, ast.Call):
            # allow only specific functions like sqrt(), mean(), median(), pow()
            if isinstance(node.func, ast.Name) and node.func.id in allowed_functions:
                fname = node.func.id
                # evaluate arguments
                try:
                    args = [eval_node(a) for a in node.args]
                except Exception as e:
                    raise ValueError(f"Invalid argument in function call: {e}")

                # flatten single list/tuple arg for functions that accept multiple values
                if len(args) == 1 and isinstance(args[0], list):
                    values = args[0]
                else:
                    values = args

                # special checks
                if fname == 'sqrt':
                    if len(values) != 1:
                        raise ValueError('sqrt() takes exactly one argument')
                    if values[0] < 0:
                        raise ValueError('Square root of negative number is not allowed')
                    return allowed_functions['sqrt'](values[0])
                if fname == 'pow':
                    if len(values) != 2:
                        raise ValueError('pow() takes exactly two arguments')
                    return allowed_functions['pow'](values[0], values[1])
                if fname in ('mean', 'avg'):
                    # mean/avg accept multiple numeric args or a single list
                    return allowed_functions['mean'](values)
                if fname == 'median':
                    return allowed_functions['median'](values)
                # fallback to other allowed functions (log, sin, etc.)
                try:
                    return allowed_functions[fname](*values)
                except TypeError:
                    raise ValueError(f"Invalid arguments for function '{fname}'")
            else:
                raise ValueError("Unsupported function call")
        else:
            raise ValueError("Invalid expression")

    node = ast.parse(expr, mode='eval').body
    return eval_node(node)

def process_input(user_input, structured=False):
    """Process a user input string.

    If structured=True, returns a dict with keys: input, success (bool), result (value or None), error (str or None).
    Otherwise returns a human-readable string (or 'exit').
    """
    raw = user_input.strip()
    l = raw.lower()
    if l in ["hi", "hello"]:
        resp = "Hello! How can I help you with math today?"
        if structured:
            return {"input": raw, "success": True, "result": None, "message": resp}
        return resp
    if "thank" in l:
        resp = "You're welcome!"
        if structured:
            return {"input": raw, "success": True, "result": None, "message": resp}
        return resp
    if l in ["exit", "quit"]:
        return "exit"

    try:
        result = safe_eval(raw)
        if structured:
            return {"input": raw, "success": True, "result": result, "error": None}
        if isinstance(result, (int, float)):
            return f"Result: {result}"
        return str(result)
    except Exception as e:
        if structured:
            return {"input": raw, "success": False, "result": None, "error": str(e)}
        return f"Error: {e}"

def main():
    print("Welcome to Math Chatbot!")
    print("I can help you with addition, subtraction, multiplication, division, and sqrt().")
    print("You can enter full math expressions (e.g., 4 + 5 * 3 or sqrt(9)).")
    print("Type 'exit' to quit.\n")

    # check for CLI flags
    json_mode = '--json' in sys.argv

    while True:
        user_input = input("You: ")
        response = process_input(user_input, structured=json_mode)
        if response == "exit":
            print("Thank you for using Math Chatbot. Goodbye!")
            break
        if json_mode:
            print(json.dumps(response))
        else:
            print("Bot:", response)

if __name__ == "__main__":
    main()
