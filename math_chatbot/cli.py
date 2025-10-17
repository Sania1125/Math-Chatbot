# math_chatbot/cli.py
from __future__ import annotations
import argparse
import json
from .evaluator import SafeEvaluator, ANGLE_MODE_DEFAULT

def main():
    parser = argparse.ArgumentParser(
        prog="mathbot",
        description="Interactive math chatbot that safely evaluates expressions."
    )
    parser.add_argument("--json", action="store_true", help="Return structured JSON objects.")
    parser.add_argument("--angle", choices=["deg", "rad"], default=ANGLE_MODE_DEFAULT,
                        help="Interpret bare trig arguments in degrees or radians (default: rad).")
    parser.add_argument("-c", "--command", metavar="EXPR",
                        help="Evaluate a single expression (non-interactive) and exit.")
    args = parser.parse_args()

    bot = SafeEvaluator(angle_mode=args.angle)

    if args.command:
        res = bot.process_input(args.command, structured=args.json)
        if args.json and res != "exit":
            # res is EvalResult
            print(json.dumps(res.__dict__, ensure_ascii=False))
        else:
            print(res)
        return

    print("Welcome to Math Chatbot!")
    print("Enter math expressions (e.g., 4 + 5 * 3, sqrt(9), sin(30) ).")
    print(f"Angle mode: {args.angle} | JSON: {args.json} | Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        response = bot.process_input(user_input, structured=args.json)
        if response == "exit":
            print("Thank you for using Math Chatbot. Goodbye!")
            break
        if args.json and hasattr(response, "__dict__"):
            print(json.dumps(response.__dict__, ensure_ascii=False))
        else:
            print("Bot:", response)
