# Import the start function from the log_watcher module inside the parser package
from backend.parser.log_watcher import start

# Entry point guard — this block only runs when the file is executed directly (not imported)
if __name__ == "__main__":
    # Wrap the entire execution in a try/except to catch Ctrl+C (KeyboardInterrupt) gracefully
    try:
        # Call the start() function to begin watching the Cowrie log file for new attack events
        start()
    except KeyboardInterrupt:
        # If the user presses Ctrl+C, print a clean shutdown message instead of a traceback
        print("Watcher stopped.")
