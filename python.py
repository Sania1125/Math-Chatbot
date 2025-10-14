
import ast
import operator

def safe_eval(expr):
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg
    }

    def eval_node(node):
        if isinstance(node, ast.Num):
            return node.n
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
        else:
            raise ValueError("Invalid expression")

    try:
        node = ast.parse(expr, mode='eval').body
        return eval_node(node)
    except Exception:
        return "Sorry, I couldn't understand or solve that expression."

def process_input(user_input):
    user_input = user_input.lower().strip()
    if user_input in ["hi", "hello"]:
        return "Hello! How can I help you with math today?"
    if "thank" in user_input:
        return "You're welcome!"
    if user_input in ["exit", "quit"]:
        return "exit"

    result = safe_eval(user_input)
    if isinstance(result, (int, float)):
        return f"Result: {result}"
    else:
        return result

def main():
    print("Welcome to Math Chatbot!")
    print("I can help you with addition, subtraction, multiplication, and division.")
    print("You can enter full math expressions (e.g., 4 + 5 * 3).")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        response = process_input(user_input)
        if response == "exit":
            print("Thank you for using Math Chatbot. Goodbye!")
            break
        print("Bot:", response)

if __name__ == "__main__":
    main()
