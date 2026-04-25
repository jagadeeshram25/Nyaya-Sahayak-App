
import sys
from rag.answer_generator import RAGController

def main():
    print("Initializing Nyaya-Sahayak... (Loading Vector Store)")
    try:
        controller = RAGController()
        print("\n=== Nyaya-Sahayak: BNS Legal Assistant ===")
        print("Type 'exit' or 'quit' to stop.\n")
    except Exception as e:
        print(f"\nError initializing system: {e}")
        print("Make sure you have run 'data_ingestion/load_bns_pdf.py' and 'indexing/build_index.py' first.")
        return

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
                
            print("Nyaya-Sahayak: Thinking...")
            answer = controller.ask_question(user_input)
            print(f"\nNyaya-Sahayak: {answer}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
