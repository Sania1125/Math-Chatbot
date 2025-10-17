import importlib.util

path = r"c:\Users\BZU\OneDrive\Desktop\vs code files\Math-Chatbot\python.py"
spec = importlib.util.spec_from_file_location("mod", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

cases = [
    'sqrt(9)',
    'sqrt(-1)',
    '4+5*3',
    'pow(2,3)',
    '2**3',
    '50% * 200',
    'mean(1,2,3)',
    'mean([1,2,3])',
    'median(1,3,2,4)'
]

for c in cases:
    print('Input:', c)
    print('Output:', mod.safe_eval(c))
