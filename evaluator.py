# math_chatbot/evaluator.py
from __future__ import annotations
import ast
import operator
import math
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Sequence, Union

Number = Union[int, float]

# ---- configuration ---------------------------------------------------------

MAX_POWER_EXPONENT = 12         # safety: cap huge exponentiations
MAX_FACTORIAL_N = 200           # safety: block gigantic factorials
ANGLE_MODE_DEFAULT = "rad"      # "deg" or "rad"

# ---- utilities -------------------------------------------------------------

def _replace_percentages(s: str) -> str:
    """Turn '50%' -> '0.5' and '12.5%' -> '0.125'."""
    def repl(m):
        num = float(m.group(1))
        return str(num / 100.0)
    return re.sub(r"(\d+(?:\.\d+)?)%", repl, s)

def _normalize_trig_shorthand(expr: str, angle_mode: str) -> str:
    """
    Support 'sin60' or 'cos 45' and optional '°'.
    If angle_mode == 'deg', bare numbers to trig are treated as degrees.
    Explicit '°' always means degrees regardless of angle_mode.
    """
    # convert '60°' -> '(60 * pi / 180)'
    expr = re.sub(
        r"(\d+(?:\.\d+)?)\s*°",
        lambda m: f"({m.group(1)} * pi / 180)",
        expr
    )

    # 'sin60' or 'cos 45' (no parentheses)
    def shorthand_to_call(m):
        fn, num = m.group(1), m.group(2)
        if angle_mode == "deg":
            return f"{fn}({num} * pi / 180)"
        return f"{fn}({num})"

    expr = re.sub(
        r"\b(sin|cos|tan)\s*\(?\s*(-?\d+(?:\.\d+)?)\s*\)?",
        shorthand_to_call,
        expr,
        flags=re.IGNORECASE
    )

    # If user wrote sin(30+15) and angle_mode is deg, convert inside to radians.
    if angle_mode == "deg":
        expr = re.sub(
            r"\b(sin|cos|tan)\s*\(\s*([0-9\.\s\+\-\*\/\(\)]+)\s*\)",
            lambda m: f"{m.group(1)}(({m.group(2)}) * pi / 180)",
            expr,
            flags=re.IGNORECASE
        )
    return expr

# ---- evaluator -------------------------------------------------------------

_ALLOWED_BIN_OPS: Dict[type, Callable[[Number, Number], Number]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_ALLOWED_UNARY_OPS: Dict[type, Callable[[Number], Number]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

def _mean(values: Sequence[Number]) -> float:
    if not values:
        raise ValueError("mean()/avg() requires at least one value")
    return float(sum(values)) / len(values)

def _median(values: Sequence[Number]) -> float:
    if not values:
        raise ValueError("median() requires at least one value")
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return float(s[mid])
    return float(s[mid - 1] + s[mid]) / 2.0

def _variance(values: Sequence[Number], ddof: int = 0) -> float:
    if not values:
        raise ValueError("var() requires at least one value")
    m = _mean(values)
    return float(sum((x - m) ** 2 for x in values)) / (len(values) - ddof or 1)

def _std(values: Sequence[Number], ddof: int = 0) -> float:
    return math.sqrt(_variance(values, ddof=ddof))

_ALLOWED_FUNCS_BASE: Dict[str, Callable[..., Number]] = {
    # arithmetic
    "sqrt": math.sqrt,
    "pow": math.pow,
    "abs": abs,
    "floor": math.floor,
    "ceil": math.ceil,
    "round": round,

    # trig/log/exp
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "radians": math.radians,
    "log": math.log,   # natural log; log(x, base) supported by math.log
    "ln": math.log,
    "exp": math.exp,

    # stats
    "mean": _mean,
    "avg": _mean,
    "median": _median,
    "min": min,
    "max": max,
    "sum": sum,
    "var": _variance,
    "std": _std,

    # combinatorics / factorial (guarded)
    "factorial": math.factorial,
}

_ALLOWED_NAMES = {
    "pi": math.pi,
    "e": math.e
}

@dataclass
class EvalResult:
    success: bool
    result: Any = None
    error: str | None = None
    message: str | None = None
    input: str | None = None

class SafeEvaluator:
    def __init__(self, angle_mode: str = ANGLE_MODE_DEFAULT):
        if angle_mode not in {"deg", "rad"}:
            raise ValueError("angle_mode must be 'deg' or 'rad'")
        self.angle_mode = angle_mode

    def _assert_safe_pow(self, left: Number, right: Number):
        # cap huge exponentiations to avoid DoS (e.g., 9**9**9)
        if isinstance(right, (int, float)) and abs(right) > MAX_POWER_EXPONENT:
            raise ValueError(f"Exponent too large (> {MAX_POWER_EXPONENT})")

    def _assert_safe_factorial(self, n: Number):
        if not (isinstance(n, int) and n >= 0):
            raise ValueError("factorial() requires a non-negative integer")
        if n > MAX_FACTORIAL_N:
            raise ValueError(f"factorial() capped at {MAX_FACTORIAL_N}")

    def _normalize(self, expr: str) -> str:
        expr = expr.strip()
        expr = _replace_percentages(expr)
        expr = _normalize_trig_shorthand(expr, self.angle_mode)
        return expr

    def _eval_node(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Invalid constant")

        if isinstance(node, ast.Name):
            if node.id in _ALLOWED_NAMES:
                return _ALLOWED_NAMES[node.id]
            raise ValueError(f"Unsupported name: {node.id}")

        if isinstance(node, (ast.List, ast.Tuple)):
            return [self._eval_node(elt) for elt in node.elts]

        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY_OPS:
            return _ALLOWED_UNARY_OPS[type(node.op)](self._eval_node(node.operand))

        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BIN_OPS:
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            if isinstance(node.op, ast.Div) and right == 0:
                raise ZeroDivisionError("Division by zero is not allowed")
            if isinstance(node.op, ast.Pow):
                self._assert_safe_pow(left, right)
            return _ALLOWED_BIN_OPS[type(node.op)](left, right)

        if isinstance(node, ast.Call):
            # allow only simple f(x, y, ...) with Name, no attrs/kwargs
            if not isinstance(node.func, ast.Name):
                raise ValueError("Unsupported function call")
            fname = node.func.id
            if fname not in _ALLOWED_FUNCS_BASE:
                raise ValueError(f"Unsupported function: {fname}")

            if node.keywords:
                raise ValueError("Keyword arguments are not allowed")

            args = [self._eval_node(a) for a in node.args]

            # flatten single list for varargs functions (mean, median, min, max, sum, var, std)
            vararg_funcs = {"mean", "avg", "median", "min", "max", "sum", "var", "std"}
            values = args[0] if (len(args) == 1 and isinstance(args[0], list) and fname in vararg_funcs) else args

            if fname == "factorial":
                if len(values) != 1:
                    raise ValueError("factorial() takes exactly one argument")
                self._assert_safe_factorial(values[0])

            return _ALLOWED_FUNCS_BASE[fname](*values)

        # Explicitly forbid comprehensions, lambdas, attributes, subscripts, etc.
        forbidden = (
            ast.Attribute, ast.Subscript, ast.Lambda, ast.Dict, ast.Set,
            ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,
            ast.BoolOp, ast.Compare, ast.IfExp, ast.Assign, ast.AugAssign,
            ast.While, ast.For, ast.With, ast.Return, ast.FunctionDef,
            ast.ClassDef, ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal
        )
        if isinstance(node, forbidden):
            raise ValueError("Unsupported syntax")

        raise ValueError("Invalid expression")

    def safe_eval(self, expr: str) -> Any:
        norm = self._normalize(expr)
        node = ast.parse(norm, mode="eval").body
        return self._eval_node(node)

    def process_input(self, user_input: str, structured: bool = False) -> Union[str, EvalResult]:
        raw = user_input.strip()
        l = raw.lower()
        if l in {"hi", "hello"}:
            msg = "Hello! How can I help you with math today?"
            return EvalResult(True, None, None, msg, raw) if structured else msg
        if "thank" in l:
            msg = "You're welcome!"
            return EvalResult(True, None, None, msg, raw) if structured else msg
        if l in {"exit", "quit"}:
            return "exit"

        try:
            result = self.safe_eval(raw)
            if structured:
                return EvalResult(True, result, None, None, raw)
            return f"Result: {result}" if isinstance(result, (int, float)) else str(result)
        except Exception as e:
            if structured:
                return EvalResult(False, None, str(e), None, raw)
            return f"Error: {e}"
