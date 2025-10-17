import pytest
from math_chatbot.evaluator import SafeEvaluator


def test_basic_arithmetic():
    evaluator = SafeEvaluator()
    assert evaluator.evaluate("2 + 3 * 4") == 14
    assert evaluator.evaluate("10 / 2") == 5.0
    assert evaluator.evaluate("2**3") == 8


def test_percentage_and_trig():
    evaluator = SafeEvaluator()
    assert evaluator.evaluate("50% * 200") == 100.0
    result = evaluator.evaluate("sin(0)")
    assert abs(result - 0.0) < 1e-9
    result = evaluator.evaluate("cos(0)")
    assert abs(result - 1.0) < 1e-9


def test_log_and_sqrt():
    evaluator = SafeEvaluator()
    assert evaluator.evaluate("log(1)") == 0.0
    assert evaluator.evaluate("sqrt(9)") == 3.0
    with pytest.raises(ValueError):
        evaluator.evaluate("sqrt(-1)")


def test_statistics_functions():
    evaluator = SafeEvaluator()
    assert evaluator.evaluate("mean(1,2,3)") == 2.0
    assert evaluator.evaluate("median(1,3,2,4)") == 2.5
