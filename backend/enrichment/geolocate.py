# Import requests to make HTTP calls to the ip-api.com geolocation API
import requests

# Import time to add a 1-second delay between API calls and avoid rate limiting
import time

# Define the base URL template for the ip-api.com free JSON API endpoint
# Fields are restricted to only what we need to minimize response size
API_URL = "http://ip-api.com/json/{ip}?fields=country,city,lat,lon,as"

# Define the list of IP address prefixes that belong to private/internal networks
# These should never be sent to an external API as they are not routable on the internet
PRIVATE_PREFIXES = ("192.168.", "172.", "10.", "127.")


# Define a helper function that checks if a given IP address is a private/internal address
def _is_private(ip: str) -> bool:
    # Check whether the IP string starts with any of the known private network prefixes
    return ip.startswith(PRIVATE_PREFIXES)


# Define the main enrichment function — takes an IP string and returns geo information as a dict
def enrich_ip(ip: str) -> dict:
    # If the IP address is private or loopback, skip the API call entirely
    if _is_private(ip):
        # Return a dict with all fields set to None — no geo data available for private IPs
        return {
            "country": None,
            "city": None,
            "latitude": None,
            "longitude": None,
            "asn": None,
        }

    # Attempt to call the ip-api.com API — wrap in try/except to handle any network errors
    try:
        # Build the full API URL by substituting the actual IP address into the template
        url = API_URL.format(ip=ip)

        # Make a synchronous GET request to the geolocation API with a 5 second timeout
        response = requests.get(url, timeout=5)

        # Parse the JSON response body into a Python dictionary
        data = response.json()

        # Pause for 1 second after every API call to respect rate limits on the free tier
        time.sleep(1)

        # Extract and return the fields we need in the normalized structure
        return {
            # The full country name where the IP is registered (e.g., "United States")
            "country": data.get("country", None),
            # The city associated with this IP address (e.g., "San Francisco")
            "city": data.get("city", None),
            # Latitude as a float (e.g., 37.7749) for map plotting
            "latitude": data.get("lat", None),
            # Longitude as a float (e.g., -122.4194) for map plotting
            "longitude": data.get("lon", None),
            # Autonomous System Number/name — identifies the ISP or hosting provider
            "asn": data.get("as", None),
        }

    except Exception:
        # If any error occurs (network failure, timeout, bad JSON, etc.), return all Nones
        return {
            "country": None,
            "city": None,
            "latitude": None,
            "longitude": None,
            "asn": None,
        }
