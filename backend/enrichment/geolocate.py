# Import requests to make HTTP calls to the ip-api.com geolocation API
import requests

# Import time to add a 1-second delay between API calls and avoid rate limiting
import time

# Import ipaddress for correct private/public IP classification (replaces the old prefix-string bug)
import ipaddress

# Define the base URL template for the ip-api.com free JSON API endpoint
# Fields are restricted to only what we need to minimize response size
API_URL = "http://ip-api.com/json/{ip}?fields=country,city,lat,lon,as"


# Define a helper function that checks if a given IP address is a private/internal address
def _is_private(ip: str) -> bool:
    # Use the stdlib's actual RFC-1918 logic instead of a naive prefix match.
    # The old check treated ALL "172.x.x.x" as private, which wrongly caught
    # public IPs like Google (172.217.x.x) and Cloudflare (172.64-71.x.x).
    try:
        return ipaddress.ip_address(ip).is_private
    except (ValueError, TypeError):
        # Empty, None, or malformed IP — treat as unroutable, skip the API call
        return True


# Define the main enrichment function — takes an IP string and returns geo information as a dict
def enrich_ip(ip: str) -> dict:
    # If the IP address is private or loopback, skip the API call entirely
    if _is_private(ip):
        return {
            "country": None,
            "city": None,
            "latitude": None,
            "longitude": None,
            "asn": None,
        }

    try:
        url = API_URL.format(ip=ip)
        response = requests.get(url, timeout=5)
        data = response.json()
        time.sleep(1)

        return {
            "country": data.get("country", None),
            "city": data.get("city", None),
            "latitude": data.get("lat", None),
            "longitude": data.get("lon", None),
            "asn": data.get("as", None),
        }

    except Exception:
        return {
            "country": None,
            "city": None,
            "latitude": None,
            "longitude": None,
            "asn": None,
        }
