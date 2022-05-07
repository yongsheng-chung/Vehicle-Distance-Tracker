import os
import requests
import urllib.parse
import datetime

from flask import redirect, render_template, request, session
from functools import wraps

# Obtain API key in global
api_key = os.environ.get("API_KEY")

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(place):
    """Look up coordinate of place"""

    # Contact Places API
    try:
        print("Trying!")
        url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={urllib.parse.quote_plus(place)}&inputtype=textquery&fields=formatted_address%2Cname%2Cplace_id%2Cgeometry&key={api_key}"
        payload=  {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()
        print("Contacted!")
    except requests.RequestException:
        print("Failed!")
        return None

    # Parse response
    try:
        data = response.json() # Decode json into python dict
        print(type(data))
        print(data)
        print(data["candidates"][0]["formatted_address"])
        return {
            "address": data["candidates"][0]["formatted_address"],
            "name": data["candidates"][0]["name"],
            "place_id": data["candidates"][0]["place_id"],
            "latlng": data["candidates"][0]["geometry"]["location"]
        }
    except (KeyError, TypeError, ValueError):
        print("Failed to return data!")
        return None


def calculate_distance(origin, destination):
    """
    Calculate distance between origin and destination
    Return distance, coordinates of two points snapped to road?
    """
    # Contact Directions API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin=place_id:{urllib.parse.quote_plus(origin)}&destination=place_id:{urllib.parse.quote_plus(destination)}&key={api_key}"
        payload=  {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()
    except:
        return None

    # Parse response
    try:
        data = response.json() # Decode json into python dict
        print(data)
        print(data["routes"][0]["legs"][0]["distance"])
        return {
            "distance": data["routes"][0]["legs"][0]["distance"],
            "duration": data["routes"][0]["legs"][0]["duration"],
            "status": data["status"],
            # "error": data["error_message"]
        }
    except (KeyError, TypeError, ValueError):
        print("Failed to return data!")
        return None

def convert_secs(duration):
    """Convert seconds to HH:MMP:SS"""
    return str(datetime.timedelta(seconds=duration))
