import asyncio
import sys
from src.agents.master_training_planner import main as run_season_planner

# Assume you might have other standalone scripts

async def show_menu():
    print("\n" + "="*30)
    print("   AI COACHING COMMAND CENTER")
    print("="*30)
    print("1. Run Master Training Planner (Health + Season)")
    print("2. [Coming Soon] Weekly Workout Planner")
    print("3. [Coming Soon] View Training")
    print("q. Exit")
    print("-"*30)

async def main():
    while True:
        await show_menu()
        choice = input("Select an option: ").strip().lower()

        if choice == '1':
            print("\nInitializing Master Training Planner...")
            try:
                # This calls the main() function from your master_training_planner.py
                await run_season_planner()
            except Exception as e:
                print(f"An error occurred: {e}")
        
        elif choice == '2':
            print("\nFeature in development: Weekly Planning.")
        
        elif choice == '3':
            print("\nFeature in development: .")

        elif choice == 'q':
            print("Exiting Coaching. Stay safe out there!")
            break
        
        else:
            print("Invalid selection. Please try again.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(0)