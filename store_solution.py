from init_db import AlgoManager

def interactive_input(vault):
    print("\n--- 📝 Log a New Solution ---")
    title = input("Problem Title: ")
    
    print("Paste your code below (Press Ctrl+D or Ctrl+Z on Windows + Enter when finished):")
    # This captures multi-line code input
    import sys
    code = sys.stdin.read()
    
    time_comp = input("Time Complexity (e.g., O(n)): ")
    space_comp = input("Space Complexity (e.g., O(1)): ")
    
    is_good_input = input("Did you guess the complexity correctly? (y/n): ").lower()
    is_good = is_good_input == 'y'
    
    notes = None
    if not is_good:
        notes = input("What went wrong? (Notes): ")
    
    vault.add_solution(is_good, title, code, time_comp, space_comp, notes)

# To use it:
if __name__ == "__main__":
    vault = AlgoManager()
    interactive_input(vault)