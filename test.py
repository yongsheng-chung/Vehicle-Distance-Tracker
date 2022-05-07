import os
import urllib.parse
import requests
from helpers import apology, login_required, lookup, calculate_distance


# Obtain API key in global
api_key = os.environ.get("API_KEY")

origin = "2A Welman Street Launceston Tasmania Australia"
destination = "Mersey Community Hospital"

origin_info = lookup(origin)
destination_info = lookup(destination)

# o_url_1 = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={urllib.parse.quote(origin)}&inputtype=textquery&fields=formatted_address%2Cname%2Cplace_id%2Cgeometry&key={api_key}"
# o_url_2 = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={urllib.parse.quote_plus(origin)}&inputtype=textquery&fields=formatted_address%2Cname%2Cplace_id%2Cgeometry&key={api_key}"
# d_url_1 = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={urllib.parse.quote(destination)}&inputtype=textquery&fields=formatted_address%2Cname%2Cplace_id%2Cgeometry&key={api_key}"
# d_url_2 = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={urllib.parse.quote_plus(destination)}&inputtype=textquery&fields=formatted_address%2Cname%2Cplace_id%2Cgeometry&key={api_key}"

# payload = {}
# headers = {}

# response = requests.request("GET", d_url_2, headers=headers, data=payload)

print(lookup(origin))
print(destination_info)

r1 = {
    'address': '2A Welman St, Launceston TAS 7250, Australia',
    'name': '2A Welman St',
    'place_id': 'ChIJLbmjht2mcKoRuXnVQaS3ME0',
    'latlng': {'lat': -41.4365133, 'lng': 147.14384}
 }

r2 = {
    'address': 'Torquay Rd, Latrobe Tasmania 7307, Australia',
    'name': 'Mersey Community Hospital',
    'place_id': 'ChIJdZIQQxC2cmsR41C2ArlT1T4',
    'latlng': {'lat': -41.2291503, 'lng': 146.4221935}
}

distance_info = calculate_distance(r1["place_id"], r2["place_id"])
print(type(distance_info))
print(distance_info)

