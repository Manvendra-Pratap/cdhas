# Import the os module to work with file paths and file operations
import os

# Import time to add a short sleep in the main watcher loop to avoid busy-waiting
import time

# Import watchdog's FileSystemEventHandler base class — we subclass it to handle file events
from watchdog.events import FileSystemEventHandler

# Import watchdog's Observer — this is the thread that watches the filesystem for changes
from watchdog.observers import Observer

# Import our Cowrie log line parser from the parser module in the same package
from backend.parser.cowrie_parser import parse_line

# Import the IP geolocation enrichment function from the enrichment module
from backend.enrichment.geolocate import enrich_ip

# Import the MongoDB collection getter so we can insert documents into the attacks collection
from backend.db.mongo import get_collection

# Define the exact absolute path to the Cowrie JSON log file we want to watch
LOG_FILE_PATH = "/home/maanu/cdhas/cowrie/var/log/cowrie/cowrie.json"


# Define our custom event handler class that extends FileSystemEventHandler
class CowrieLogHandler(FileSystemEventHandler):

    # Constructor — called once when the handler is created
    def __init__(self):
        # Call the parent class constructor to initialize the base handler
        super().__init__()

        # Open the log file in read mode so we can track our reading position
        self._file = open(LOG_FILE_PATH, "r")

        # Seek to the END of the file — this skips all existing lines already in the file
        # Only NEW lines written after the watcher starts will be processed
        self._file.seek(0, 2)

        # Store a reference to the MongoDB attacks collection for inserting documents
        self._collection = get_collection()

    # This method is called by watchdog whenever a file modification event is detected
    def on_modified(self, event):
        # Only react to events on our specific log file — ignore any other files in the directory
        if not event.src_path.endswith("cowrie.json"):
            return

        # Read all new lines that were added since we last checked the file position
        for raw_line in self._file:
            # Use the Cowrie parser to turn the raw JSON string into a normalized Python dict
            parsed = parse_line(raw_line)

            # If the parser returned None, this line is not a recognized event type — skip it
            if parsed is None:
                continue

            # Extract the source IP from the parsed event to use for geolocation lookup
            ip = parsed.get("source_ip", "")

            # Call the geolocation API (or return None fields for private IPs)
            geo = enrich_ip(ip)

            # Merge the parsed event dict and the geo enrichment dict into a single combined dict
            # The ** unpacking operator spreads both dicts into one — geo fields are added to parsed
            combined = {**parsed, **geo}

            # Insert the combined document into the MongoDB attacks collection
            self._collection.insert_one(combined)

            # Extract the country from the geo data for the confirmation print message
            country = geo.get("country") or "Unknown"

            # Print a confirmation message to stdout for each successfully saved attack event
            print(f"Saved attack from {ip} [{country}]")


# Define the start() function — the main entry point that sets up and runs the file watcher
def start():
    # Instantiate our custom log event handler — this also opens the file and seeks to end
    event_handler = CowrieLogHandler()

    # Create a watchdog Observer — this is the background thread that monitors the filesystem
    observer = Observer()

    # Schedule the observer to watch the DIRECTORY containing our log file
    # We use the directory path because watchdog watches directories, not individual files
    # recursive=False means we only watch the top-level directory, not subdirectories
    observer.schedule(event_handler, path=os.path.dirname(LOG_FILE_PATH), recursive=False)

    # Start the observer background thread — it will now emit events when files change
    observer.start()

    # Print a startup confirmation so the user knows the watcher is running
    print(f"Watching {LOG_FILE_PATH} for new attack events...")

    # Enter an infinite loop to keep the main thread alive while the observer runs in background
    try:
        # Loop forever, sleeping 1 second at a time to keep CPU usage low
        while True:
            # Sleep for 1 second before checking again — the observer handles events in its own thread
            time.sleep(1)
    except KeyboardInterrupt:
        # If the user presses Ctrl+C, catch the interrupt and stop the observer cleanly
        observer.stop()

    # Wait for the observer thread to fully finish before returning
    observer.join()
