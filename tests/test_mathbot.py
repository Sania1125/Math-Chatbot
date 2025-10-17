import importlib.util
import math

# helper to load the module without running its interactive main
def load_module():
    path = r"c:\Users\BZU\OneDrive\Desktop\vs code files\Math-Chatbot\python.py"
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_sqrt_and_negative():
    mod = load_module()
    assert mod.safe_eval('sqrt(9)') == 3.0
    # negative sqrt should raise a ValueError when evaluated directly
    try:
        mod.safe_eval('sqrt(-1)')
        raised = False
    except Exception:
        raised = True
    assert raised


def test_power_operators():
    mod = load_module()
    assert mod.safe_eval('2**3') == 8
    assert mod.safe_eval('pow(2,3)') == 8.0


def test_percent_and_arithmetic():
    mod = load_module()
    assert mod.safe_eval('50% * 200') == 100.0
    assert mod.safe_eval('4+5*3') == 19


def test_mean_median():
    mod = load_module()
    assert mod.safe_eval('mean(1,2,3)') == 2.0
    assert mod.safe_eval('mean([1,2,3])') == 2.0
    assert mod.safe_eval('median(1,3,2,4)') == 2.5


def test_trig_and_log():
    mod = load_module()
    assert abs(mod.safe_eval('sin(0)') - 0.0) < 1e-9
    assert abs(mod.safe_eval('cos(0)') - 1.0) < 1e-9
    assert abs(mod.safe_eval('log(1)') - 0.0) < 1e-9


def test_structured_process_input():
    mod = load_module()
    r = mod.process_input('4+5', structured=True)
    assert isinstance(r, dict)
    assert r['success'] is True
    assert r['result'] == 9

    r2 = mod.process_input('sqrt(-1)', structured=True)
    assert r2['success'] is False
    assert 'error' in r2 and r2['error']
