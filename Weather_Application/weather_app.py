"""
Project Title : Weather Application using API Integration
Author        : Ardra
Description   : A command-line weather application that fetches real-time
                weather data (temperature, humidity, wind speed and weather
                condition) for any city using the OpenWeatherMap API.

                The application is organized into clearly separated layers:
                    1. API Layer       -> builds requests and talks to OpenWeatherMap
                    2. Parsing Layer   -> converts raw JSON into clean, structured data
                    3. Display Layer   -> presents the data in a readable report
                    4. Menu / Controller Layer -> ties everything together

                A built-in MOCK MODE (enabled by default) lets the whole
                program be tested and demonstrated without needing an
                internet connection or a real API key. Live mode can be
                switched on at any time from the menu once a valid
                OpenWeatherMap API key is added to CONFIG.
"""

import json
import logging
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

# --------------------------------------------------------------------------- #
# CONFIGURATION
# --------------------------------------------------------------------------- #
CONFIG = {
    "API_KEY": "YOUR_OPENWEATHERMAP_API_KEY_HERE",   # get one free at openweathermap.org
    "BASE_URL": "https://api.openweathermap.org/data/2.5/weather",
    "UNITS": "metric",                # "metric" -> Celsius, "imperial" -> Fahrenheit
    "TIMEOUT_SECONDS": 8,
    "USE_MOCK_DATA": True,            # True = works offline with no API key needed
    "LOG_FILE": "weather_app.log",
    "HISTORY_FILE": "weather_history.json",
}

# Sample offline data so the app is fully self-contained and runnable
# out-of-the-box, with no account or internet connection required.
# Includes a handful of international cities plus 50+ Indian cities so the
# mock dataset is representative of real-world, nationwide usage.
def _in(name, temp, humidity, feels_like, wind, main, desc):
    """Small helper to keep the large mock dataset below compact and readable."""
    return {
        "name": name,
        "sys": {"country": "IN"},
        "main": {"temp": temp, "humidity": humidity, "feels_like": feels_like},
        "wind": {"speed": wind},
        "weather": [{"main": main, "description": desc}],
    }


MOCK_WEATHER_DATA = {
    # International reference cities
    "london": {
        "name": "London", "sys": {"country": "GB"},
        "main": {"temp": 17.2, "humidity": 65, "feels_like": 17.0},
        "wind": {"speed": 4.1},
        "weather": [{"main": "Rain", "description": "light rain"}],
    },
    "new york": {
        "name": "New York", "sys": {"country": "US"},
        "main": {"temp": 24.8, "humidity": 55, "feels_like": 25.3},
        "wind": {"speed": 5.2},
        "weather": [{"main": "Clear", "description": "clear sky"}],
    },
    "tokyo": {
        "name": "Tokyo", "sys": {"country": "JP"},
        "main": {"temp": 27.1, "humidity": 70, "feels_like": 29.0},
        "wind": {"speed": 2.8},
        "weather": [{"main": "Clouds", "description": "overcast clouds"}],
    },

    # Indian cities (50+)
    "thiruvananthapuram": _in("Thiruvananthapuram", 29.5, 78, 33.1, 3.6, "Clouds", "scattered clouds"),
    "mumbai": _in("Mumbai", 31.4, 74, 35.0, 4.3, "Clouds", "broken clouds"),
    "delhi": _in("Delhi", 34.2, 40, 33.5, 3.1, "Haze", "haze"),
    "bengaluru": _in("Bengaluru", 24.6, 60, 25.0, 3.8, "Clouds", "few clouds"),
    "chennai": _in("Chennai", 33.8, 68, 38.2, 4.6, "Clear", "clear sky"),
    "kolkata": _in("Kolkata", 32.1, 80, 37.0, 3.3, "Rain", "moderate rain"),
    "hyderabad": _in("Hyderabad", 28.9, 55, 29.3, 3.9, "Clouds", "scattered clouds"),
    "pune": _in("Pune", 27.3, 58, 27.9, 3.4, "Clear", "clear sky"),
    "ahmedabad": _in("Ahmedabad", 33.6, 45, 32.8, 2.9, "Clear", "clear sky"),
    "jaipur": _in("Jaipur", 32.0, 38, 31.2, 3.0, "Clear", "clear sky"),
    "surat": _in("Surat", 31.8, 70, 35.5, 3.5, "Clouds", "scattered clouds"),
    "lucknow": _in("Lucknow", 30.5, 50, 30.9, 2.7, "Haze", "haze"),
    "kanpur": _in("Kanpur", 31.2, 48, 31.6, 2.8, "Haze", "haze"),
    "nagpur": _in("Nagpur", 30.9, 42, 30.3, 3.2, "Clear", "clear sky"),
    "indore": _in("Indore", 29.4, 44, 29.0, 3.1, "Clouds", "few clouds"),
    "thane": _in("Thane", 30.7, 76, 34.9, 4.1, "Clouds", "broken clouds"),
    "bhopal": _in("Bhopal", 28.6, 46, 28.2, 3.0, "Clear", "clear sky"),
    "visakhapatnam": _in("Visakhapatnam", 30.2, 72, 34.5, 5.0, "Clouds", "scattered clouds"),
    "vadodara": _in("Vadodara", 31.5, 60, 33.8, 2.9, "Clouds", "few clouds"),
    "firozabad": _in("Firozabad", 30.8, 47, 31.0, 2.6, "Haze", "haze"),
    "ludhiana": _in("Ludhiana", 29.9, 42, 29.5, 2.7, "Clear", "clear sky"),
    "agra": _in("Agra", 31.9, 40, 31.4, 2.8, "Haze", "haze"),
    "nashik": _in("Nashik", 27.8, 55, 27.5, 3.3, "Clear", "clear sky"),
    "faridabad": _in("Faridabad", 33.4, 39, 32.7, 3.0, "Haze", "haze"),
    "meerut": _in("Meerut", 31.6, 44, 31.9, 2.6, "Haze", "haze"),
    "rajkot": _in("Rajkot", 32.7, 48, 32.2, 3.1, "Clear", "clear sky"),
    "kalyan": _in("Kalyan", 30.4, 74, 34.2, 4.0, "Clouds", "broken clouds"),
    "vasai": _in("Vasai-Virar", 30.1, 75, 34.0, 4.2, "Clouds", "broken clouds"),
    "varanasi": _in("Varanasi", 31.1, 55, 32.0, 2.9, "Haze", "haze"),
    "srinagar": _in("Srinagar", 18.4, 50, 17.9, 2.2, "Clear", "clear sky"),
    "aurangabad": _in("Aurangabad", 29.6, 50, 29.2, 3.2, "Clear", "clear sky"),
    "dhanbad": _in("Dhanbad", 29.8, 58, 30.5, 2.8, "Clouds", "few clouds"),
    "amritsar": _in("Amritsar", 30.3, 41, 29.9, 2.5, "Clear", "clear sky"),
    "navi mumbai": _in("Navi Mumbai", 30.9, 76, 35.1, 4.0, "Clouds", "broken clouds"),
    "allahabad": _in("Prayagraj", 31.4, 46, 31.7, 2.7, "Haze", "haze"),
    "ranchi": _in("Ranchi", 27.5, 60, 27.8, 3.0, "Clouds", "scattered clouds"),
    "howrah": _in("Howrah", 32.0, 79, 36.8, 3.2, "Rain", "moderate rain"),
    "coimbatore": _in("Coimbatore", 28.7, 62, 29.5, 3.5, "Clouds", "few clouds"),
    "jabalpur": _in("Jabalpur", 29.2, 48, 28.8, 2.9, "Clear", "clear sky"),
    "gwalior": _in("Gwalior", 32.3, 40, 31.8, 2.8, "Clear", "clear sky"),
    "vijayawada": _in("Vijayawada", 32.5, 65, 36.9, 3.6, "Clouds", "scattered clouds"),
    "jodhpur": _in("Jodhpur", 33.1, 30, 31.9, 3.4, "Clear", "clear sky"),
    "madurai": _in("Madurai", 31.6, 60, 34.2, 3.7, "Clear", "clear sky"),
    "raipur": _in("Raipur", 30.6, 52, 31.0, 3.0, "Clouds", "few clouds"),
    "kota": _in("Kota", 32.8, 35, 31.5, 2.9, "Clear", "clear sky"),
    "guwahati": _in("Guwahati", 28.9, 82, 32.5, 2.6, "Rain", "moderate rain"),
    "chandigarh": _in("Chandigarh", 30.0, 44, 29.6, 2.7, "Clear", "clear sky"),
    "solapur": _in("Solapur", 30.3, 46, 29.9, 3.3, "Clear", "clear sky"),
    "bareilly": _in("Bareilly", 30.9, 45, 31.2, 2.5, "Haze", "haze"),
    "mysuru": _in("Mysuru", 25.8, 58, 26.1, 3.4, "Clouds", "few clouds"),
    "tiruchirappalli": _in("Tiruchirappalli", 32.4, 58, 36.0, 3.8, "Clear", "clear sky"),
    "bhubaneswar": _in("Bhubaneswar", 31.9, 74, 36.5, 3.5, "Clouds", "scattered clouds"),
    "salem": _in("Salem", 29.5, 55, 29.9, 3.2, "Clear", "clear sky"),
    "warangal": _in("Warangal", 30.1, 50, 30.6, 3.1, "Clear", "clear sky"),
    "thiruvananthapuram alt": None,  # placeholder removed below
    "guntur": _in("Guntur", 32.8, 63, 37.1, 3.6, "Clouds", "scattered clouds"),
    "amravati": _in("Amravati", 30.4, 45, 30.0, 3.0, "Clear", "clear sky"),
    "kochi": _in("Kochi", 29.8, 80, 34.5, 3.9, "Rain", "light rain"),
    "kozhikode": _in("Kozhikode", 29.3, 79, 33.8, 3.7, "Clouds", "scattered clouds"),
    "thrissur": _in("Thrissur", 29.6, 77, 33.5, 3.5, "Clouds", "few clouds"),
    "shimla": _in("Shimla", 19.2, 55, 18.6, 2.1, "Clouds", "scattered clouds"),
    "dehradun": _in("Dehradun", 27.4, 58, 27.0, 2.4, "Clouds", "few clouds"),
    "goa": _in("Panaji", 30.5, 78, 34.9, 4.4, "Rain", "light rain"),
}

# remove the placeholder helper key used only for readability above
MOCK_WEATHER_DATA.pop("thiruvananthapuram alt", None)

# --------------------------------------------------------------------------- #
# LOGGING SETUP (timestamped, console + file)
# --------------------------------------------------------------------------- #
logger = logging.getLogger("weather_app")
logger.setLevel(logging.DEBUG)

_formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setLevel(logging.INFO)
_console_handler.setFormatter(_formatter)

_file_handler = logging.FileHandler(CONFIG["LOG_FILE"], encoding="utf-8")
_file_handler.setLevel(logging.DEBUG)
_file_handler.setFormatter(_formatter)

logger.addHandler(_console_handler)
logger.addHandler(_file_handler)


# --------------------------------------------------------------------------- #
# CUSTOM EXCEPTIONS
# --------------------------------------------------------------------------- #
class WeatherAPIError(Exception):
    """Base exception for all weather-fetching related errors."""


class InvalidAPIKeyError(WeatherAPIError):
    """Raised when the API rejects the request due to a bad/missing key."""


class CityNotFoundError(WeatherAPIError):
    """Raised when the requested city cannot be found."""


class NetworkError(WeatherAPIError):
    """Raised when the request fails due to connectivity/timeout issues."""


# --------------------------------------------------------------------------- #
# 1. API LAYER  -  responsible ONLY for fetching raw data
# --------------------------------------------------------------------------- #
def fetch_weather_data(city: str) -> dict:
    """
    Fetch raw weather data for a given city.

    Uses mock/offline data when CONFIG["USE_MOCK_DATA"] is True, otherwise
    performs a real HTTP request to the OpenWeatherMap API.

    Returns the raw JSON response as a Python dictionary.
    Raises WeatherAPIError subclasses on failure.
    """
    city_clean = city.strip()
    if not city_clean:
        raise ValueError("City name cannot be empty.")

    if CONFIG["USE_MOCK_DATA"]:
        return _fetch_mock_weather(city_clean)
    return _fetch_live_weather(city_clean)


def _fetch_mock_weather(city: str) -> dict:
    """Simulates an API call using the local MOCK_WEATHER_DATA dictionary."""
    logger.debug("Fetching MOCK weather data for '%s'", city)
    key = city.lower()
    if key not in MOCK_WEATHER_DATA:
        logger.warning("City '%s' not found in mock dataset", city)
        raise CityNotFoundError(
            f"'{city}' was not found. Try one of: "
            f"{', '.join(name.title() for name in MOCK_WEATHER_DATA)}"
        )
    return MOCK_WEATHER_DATA[key]


def _fetch_live_weather(city: str) -> dict:
    """Performs the real HTTP GET request against the OpenWeatherMap API."""
    if not CONFIG["API_KEY"] or CONFIG["API_KEY"] == "YOUR_OPENWEATHERMAP_API_KEY_HERE":
        raise InvalidAPIKeyError(
            "No valid API key configured. Set CONFIG['API_KEY'] or switch to mock mode."
        )

    params = {
        "q": city,
        "appid": CONFIG["API_KEY"],
        "units": CONFIG["UNITS"],
    }
    url = f"{CONFIG['BASE_URL']}?{urllib.parse.urlencode(params)}"
    logger.debug("Requesting live weather data from: %s", url)

    try:
        with urllib.request.urlopen(url, timeout=CONFIG["TIMEOUT_SECONDS"]) as response:
            raw_bytes = response.read()
            return json.loads(raw_bytes.decode("utf-8"))

    except urllib.error.HTTPError as http_err:
        if http_err.code == 401:
            raise InvalidAPIKeyError("The API rejected the request: invalid API key.") from http_err
        if http_err.code == 404:
            raise CityNotFoundError(f"'{city}' could not be found by the weather service.") from http_err
        raise WeatherAPIError(f"HTTP error {http_err.code}: {http_err.reason}") from http_err

    except urllib.error.URLError as url_err:
        raise NetworkError(f"Network error while contacting weather service: {url_err.reason}") from url_err

    except TimeoutError as timeout_err:
        raise NetworkError("The request timed out. Please check your connection.") from timeout_err

    except json.JSONDecodeError as decode_err:
        raise WeatherAPIError("Received an invalid response from the weather service.") from decode_err


# --------------------------------------------------------------------------- #
# 2. PARSING LAYER  -  responsible ONLY for turning raw JSON into clean data
# --------------------------------------------------------------------------- #
def parse_weather_data(raw_data: dict) -> dict:
    """
    Extracts and normalizes the fields the application cares about:
    city name, country, temperature, feels-like, humidity, wind speed,
    and a human-readable condition description.
    """
    try:
        return {
            "city": raw_data["name"],
            "country": raw_data.get("sys", {}).get("country", "N/A"),
            "temperature": raw_data["main"]["temp"],
            "feels_like": raw_data["main"].get("feels_like", raw_data["main"]["temp"]),
            "humidity": raw_data["main"]["humidity"],
            "wind_speed": raw_data["wind"]["speed"],
            "condition": raw_data["weather"][0]["main"],
            "description": raw_data["weather"][0]["description"].title(),
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    except (KeyError, IndexError) as parse_err:
        logger.error("Malformed weather payload: %s", parse_err)
        raise WeatherAPIError("Weather data was missing expected fields.") from parse_err


# --------------------------------------------------------------------------- #
# 3. DISPLAY LAYER  -  responsible ONLY for presenting parsed data
# --------------------------------------------------------------------------- #
def display_weather(parsed: dict) -> None:
    """Prints a clean, user-friendly weather report to the console."""
    unit_symbol = "\u00b0C" if CONFIG["UNITS"] == "metric" else "\u00b0F"
    speed_unit = "m/s" if CONFIG["UNITS"] == "metric" else "mph"

    print("\n" + "=" * 44)
    print(f"  WEATHER REPORT: {parsed['city']}, {parsed['country']}")
    print("=" * 44)
    print(f"  Condition     : {parsed['condition']} ({parsed['description']})")
    print(f"  Temperature   : {parsed['temperature']}{unit_symbol}")
    print(f"  Feels Like    : {parsed['feels_like']}{unit_symbol}")
    print(f"  Humidity      : {parsed['humidity']}%")
    print(f"  Wind Speed    : {parsed['wind_speed']} {speed_unit}")
    print(f"  Retrieved At  : {parsed['fetched_at']}")
    print("=" * 44 + "\n")


# --------------------------------------------------------------------------- #
# HISTORY HELPERS (JSON persistence of past searches)
# --------------------------------------------------------------------------- #
def save_to_history(parsed: dict) -> None:
    """Appends a parsed weather record to the local JSON history file."""
    history = load_history()
    history.append(parsed)
    try:
        with open(CONFIG["HISTORY_FILE"], "w", encoding="utf-8") as file:
            json.dump(history, file, indent=2)
        logger.debug("Saved search for '%s' to history", parsed["city"])
    except OSError as os_err:
        logger.warning("Could not write history file: %s", os_err)


def load_history() -> list:
    """Loads previous search history from disk, returning [] if unavailable."""
    if not os.path.exists(CONFIG["HISTORY_FILE"]):
        return []
    try:
        with open(CONFIG["HISTORY_FILE"], "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as err:
        logger.warning("Could not read history file, starting fresh: %s", err)
        return []


def display_history() -> None:
    """Shows all past searches in a simple numbered list."""
    history = load_history()
    if not history:
        print("\nNo search history yet.\n")
        return

    print("\n" + "-" * 44)
    print("  SEARCH HISTORY")
    print("-" * 44)
    for index, record in enumerate(history, start=1):
        print(
            f"  {index}. {record['city']}, {record['country']} - "
            f"{record['temperature']}\u00b0 {record['condition']} "
            f"(at {record['fetched_at']})"
        )
    print("-" * 44 + "\n")


# --------------------------------------------------------------------------- #
# CONTROLLER LAYER  -  ties API, parsing and display together
# --------------------------------------------------------------------------- #
def get_weather_for_city(city: str) -> None:
    """Runs the full fetch -> parse -> display -> save pipeline for one city."""
    try:
        logger.info("Looking up weather for '%s'", city)
        raw_data = fetch_weather_data(city)
        parsed = parse_weather_data(raw_data)
        display_weather(parsed)
        save_to_history(parsed)
        logger.info("Successfully displayed weather for '%s'", parsed["city"])

    except CityNotFoundError as err:
        logger.warning("City not found: %s", err)
        print(f"\n[!] {err}\n")

    except InvalidAPIKeyError as err:
        logger.error("API key problem: %s", err)
        print(f"\n[!] {err}\n")

    except NetworkError as err:
        logger.error("Network problem: %s", err)
        print(f"\n[!] {err}\n")

    except WeatherAPIError as err:
        logger.error("Weather API error: %s", err)
        print(f"\n[!] Something went wrong: {err}\n")

    except ValueError as err:
        print(f"\n[!] {err}\n")


def toggle_units() -> None:
    """Switches temperature/wind units between metric and imperial."""
    CONFIG["UNITS"] = "imperial" if CONFIG["UNITS"] == "metric" else "metric"
    logger.info("Units switched to '%s'", CONFIG["UNITS"])
    print(f"\nUnits changed to: {CONFIG['UNITS'].upper()}\n")


def toggle_mode() -> None:
    """Switches between offline mock mode and live API mode."""
    CONFIG["USE_MOCK_DATA"] = not CONFIG["USE_MOCK_DATA"]
    mode = "MOCK (offline)" if CONFIG["USE_MOCK_DATA"] else "LIVE (real API)"
    logger.info("Data source switched to %s mode", mode)
    print(f"\nData source is now: {mode}\n")
    if not CONFIG["USE_MOCK_DATA"]:
        print("Reminder: set a valid CONFIG['API_KEY'] for live mode to work.\n")


# --------------------------------------------------------------------------- #
# MENU / ENTRY POINT
# --------------------------------------------------------------------------- #
def print_menu() -> None:
    mode = "MOCK" if CONFIG["USE_MOCK_DATA"] else "LIVE"
    print("=" * 44)
    print("       WEATHER APPLICATION")
    print(f"       (mode: {mode} | units: {CONFIG['UNITS']})")
    print("=" * 44)
    print("  1. Get weather for a city")
    print("  2. View search history")
    print("  3. Toggle temperature units (C/F)")
    print("  4. Toggle mock/live data source")
    print("  5. Exit")
    print("=" * 44)


def main() -> None:
    logger.info("Weather Application started")
    print("\nWelcome to the Weather Application!")
    if CONFIG["USE_MOCK_DATA"]:
        print(
            "Running in MOCK mode - 60+ Indian cities available "
            "(e.g. Mumbai, Delhi, Bengaluru, Chennai, Kolkata, Kochi) "
            "plus London, New York, Tokyo\n"
        )

    while True:
        print_menu()
        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            city = input("Enter city name: ").strip()
            get_weather_for_city(city)

        elif choice == "2":
            display_history()

        elif choice == "3":
            toggle_units()

        elif choice == "4":
            toggle_mode()

        elif choice == "5":
            logger.info("Weather Application exited by user")
            print("\nGoodbye!\n")
            break

        else:
            print("\n[!] Invalid choice. Please enter a number from 1 to 5.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Weather Application interrupted by user (Ctrl+C)")
        print("\n\nInterrupted. Goodbye!\n")
        sys.exit(0)
