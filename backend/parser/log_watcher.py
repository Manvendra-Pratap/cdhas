# Import the os module to work with file paths and file operations
import os

# Import time to add a short sleep in the main watcher loop to avoid busy-waiting
import time

# Import threading/queue so geo enrichment can run off the ingestion critical path.
# Previously enrich_ip() (HTTP call + 1s sleep) ran synchronously inside on_modified,
# which meant a burst of attack events would queue up behind the rate-limited API call.
import threading
import queue

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

# Path to the Cowrie JSON log file — configurable per machine via env var, since every
# teammate's Cowrie install lives at a different path. Falls back to Maanu's original
# path only as a default for local dev.
LOG_FILE_PATH = os.environ.get(
    "CDHAS_COWRIE_LOG_PATH",
    "/home/maanu/cdhas/cowrie/var/log/cowrie/cowrie.json",
)


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

        # Bounded queue of (mongo_id, ip) pairs waiting for geo enrichment. Bounded so a
        # huge burst can't grow this unbounded in memory — worker just falls behind, doesn't crash.
        self._enrich_queue = queue.Queue(maxsize=10000)

        # Background thread that drains the queue and does the slow (rate-limited) geo calls,
        # completely off the ingestion path. daemon=True so it doesn't block process exit.
        self._enrich_thread = threading.Thread(target=self._enrichment_worker, daemon=True)
        self._enrich_thread.start()

    # Runs forever in a background thread: pulls (doc_id, ip) off the queue, calls the
    # rate-limited geo API, then patches just the geo fields onto the already-inserted doc.
    def _enrichment_worker(self):
        while True:
            doc_id, ip = self._enrich_queue.get()
            geo = enrich_ip(ip)
            self._collection.update_one({"_id": doc_id}, {"$set": geo})
            country = geo.get("country") or "Unknown"
            print(f"Enriched attack from {ip} [{country}]")

    # This method is called by watchdog whenever a file modification event is detected
    def on_modified(self, event):
        # Only react to events on our specific log file — ignore any other files in the directory
        if event.src_path != LOG_FILE_PATH:
            return

        # Read all new lines added since we last checked. Using readline() in a loop
        # instead of "for line in self._file" — the file-iterator form does internal
        # readahead buffering that behaves unreliably on a file that's actively growing
        # (can miss lines across separate on_modified calls). readline() has no such issue.
        while True:
            raw_line = self._file.readline()
            if not raw_line:
                break

            # Use the Cowrie parser to turn the raw JSON string into a normalized Python dict
            parsed = parse_line(raw_line)

            # If the parser returned None, this line is not a recognized event type — skip it
            if parsed is None:
                continue

            # Extract the source IP from the parsed event to use for geolocation lookup
            ip = parsed.get("source_ip", "")

            # Insert the RAW parsed event immediately — no waiting on the geo API.
            # Geo fields will be missing until the background worker patches them in.
            result = self._collection.insert_one(parsed)

            # Hand the new doc's _id and IP off to the background enrichment worker.
            # If the queue is full (extreme burst), drop enrichment for this one rather
            # than blocking ingestion — losing a geo lookup is better than losing the event.
            try:
                self._enrich_queue.put_nowait((result.inserted_id, ip))
            except queue.Full:
                print(f"Enrichment queue full — skipping geo lookup for {ip}")

            # Print a confirmation message to stdout for each successfully saved attack event
            print(f"Saved attack from {ip} (enrichment queued)")


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
