# tests/test_evaluator.py
from math_chatbot.evaluator import SafeEvaluator
import math
import pytest

def make():
    return SafeEvaluator(angle_mode="rad")

def test_sqrt_and_negative():
    bot = make()
    assert bot.safe_eval('sqrt(9)') == 3.0
    with pytest.raises(ValueError):
        bot.safe_eval('sqrt(-1)')

def test_power_operators_and_limits():
    bot = make()
    assert bot.safe_eval('2**3') == 8
    assert bot.safe_eval('pow(2,3)') == 8.0
    with pytest.raises(ValueError):
        bot.safe_eval('2**1000')  # beyond MAX_POWER_EXPONENT

def test_percent_and_arithmetic():
    bot = make()
    assert bot.safe_eval('50% * 200') == 100.0
    assert bot.safe_eval('4+5*3') == 19

def test_mean_median_min_max_sum():
    bot = make()
    assert bot.safe_eval('mean(1,2,3)') == 2.0
    assert bot.safe_eval('mean([1,2,3])') == 2.0
    assert bot.safe_eval('median(1,3,2,4)') == 2.5
    assert bot.safe_eval('min(3,1,4)') == 1
    assert bot.safe_eval('max([3,1,4])') == 4
    assert bot.safe_eval('sum([1,2,3])') == 6

def test_var_std():
    bot = make()
    assert bot.safe_eval('round(var([1,2,3]), 6)') == round(((1-2)**2+(2-2)**2+(3-2)**2)/3, 6)
    assert bot.safe_eval('round(std([1,2,3]), 6)') == round(math.sqrt(2/3), 6)

def test_trig_and_log_rad():
    bot = SafeEvaluator(angle_mode="rad")
    assert abs(bot.safe_eval('sin(0)') - 0.0) < 1e-9
    assert abs(bot.safe_eval('cos(0)') - 1.0) < 1e-9
    assert abs(bot.safe_eval('log(1)') - 0.0) < 1e-9

def test_trig_degrees_mode_and_symbols():
    bot = SafeEvaluator(angle_mode="deg")
    assert abs(bot.safe_eval('sin(30)') - 0.5) < 1e-9
    assert abs(bot.safe_eval('cos 60') - 0.5) < 1e-9
    assert abs(bot.safe_eval('tan 45') - 1.0) < 1e-9
    assert abs(bot.safe_eval('sin(30+30)') - 1.0) < 1e-9
    assert abs(bot.safe_eval('sin 90°') - 1.0) < 1e-9

def test_division_by_zero():
    bot = make()
    with pytest.raises(ZeroDivisionError):
        bot.safe_eval('1/0')

def test_factorial_limits():
    bot = make()
    assert bot.safe_eval('factorial(5)') == 120
    with pytest.raises(ValueError):
        bot.safe_eval('factorial(-1)')
