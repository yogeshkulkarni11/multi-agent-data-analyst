from .agents import ask


def main() -> None:
    print("Multi-Agent Data Analyst")
    print("Examples: What is total revenue? | Show revenue by region | What are monthly sales?")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        state = ask(question)
        print(f"\nAssistant:\n{state.get('answer', 'No answer generated.')}")


if __name__ == "__main__":
    main()
