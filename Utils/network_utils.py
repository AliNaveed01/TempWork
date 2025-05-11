import random
import time 
import logging
import requests
import functools
# Updated PROXIES List with Elite HTTPS Proxies
PROXIES = [
    "http://44.219.175.186:80",     # US (Elite Proxy, HTTPS)
    "http://204.236.137.68:80",     # US (Elite Proxy, HTTPS)
    "http://179.96.28.58:80",       # Brazil (Elite Proxy, HTTPS)
    "http://63.35.64.177:3128",     # Ireland (Elite Proxy, HTTPS)
    "http://54.152.3.36:80",        # US (Elite Proxy, HTTPS)
    "http://3.212.148.199:3128",    # US (Elite Proxy, HTTPS)
    "http://51.20.19.159:3128",     # Sweden (Elite Proxy, HTTPS)
    "http://13.55.210.141:3128",    # Australia (Elite Proxy, HTTPS)
    "http://16.16.239.39:3128"      # (Country Unknown) (Elite Proxy, HTTPS)
]


CONSECUTIVE_FAILURES = 0
CIRCUIT_BREAK_THRESHOLD = 7  # Stop requests if 5 fail in a row
CIRCUIT_BREAK_TIMEOUT = 120  # 


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 15_2 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Edge/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Android 11; Mobile; rv:99.0) Gecko/99.0 Firefox/99.0",
    "Mozilla/5.0 (Android 10; Mobile; SamsungBrowser/16.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Android 12; Mobile; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Android 13; Mobile; OnePlus 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
]



def get_random_proxy():
    """
    Selects a random proxy from the list of free proxies.
    """
    proxy = random.choice(PROXIES)
    return {"http": proxy, "https": proxy}


def get_random_headers():
    return {
        'accept': '*/*',
        'user-agent': random.choice(USER_AGENTS),  # Rotating user agents
        'accept-language': random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.9", "en-GB,en-US;q=0.8,en;q=0.7"]),
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.allsop.co.uk/property-search?available_only=true&lot_type=commercial&size=100',
    }



def circuit_breaker():
    """
    Implements a basic circuit breaker mechanism.
    If too many consecutive requests fail, it stops making requests for a while.
    """
    global CONSECUTIVE_FAILURES

    if CONSECUTIVE_FAILURES >= CIRCUIT_BREAK_THRESHOLD:
        logging.warning(f" Circuit Breaker Activated! Too many failures ({CONSECUTIVE_FAILURES}). Pausing for {CIRCUIT_BREAK_TIMEOUT} seconds.")
        time.sleep(CIRCUIT_BREAK_TIMEOUT)  # Pause execution
        CONSECUTIVE_FAILURES = 0  # Reset failure count


def make_request_with_backoff(url, headers = None, max_retries=5):
    """
    Makes an API request with exponential backoff.
    Retries up to `max_retries` times before failing.
    """
    global CONSECUTIVE_FAILURES
    attempt = 0
    delay = 1  # Start with 1 second

    # proxy = get_random_proxy()

    while attempt < max_retries:
        try:


            # proxy = get_random_proxy()  # Get a new free proxy
            # logging.info(f" Using Proxy: {proxy['http']}")

            response = requests.get(url, headers=get_random_headers(), timeout=10)
        
            if response.status_code == 200:
                CONSECUTIVE_FAILURES = 0  # Reset failure count on success
                return response.json()
            else:
                logging.warning(f"Attempt {attempt + 1}: Received status {response.status_code} for {url}")
        except requests.RequestException as e:
            logging.error(f"Attempt {attempt + 1}: Request failed due to {e}")

        # Wait before retrying
        time.sleep(delay)
        delay *= 2  # Double the wait time (Exponential Backoff)
        attempt += 1

    CONSECUTIVE_FAILURES += 1  # Increment failure count if request completely fails
    logging.error(f"Request failed after {max_retries} retries: {url}")
    return None  # Return None if all retries fail