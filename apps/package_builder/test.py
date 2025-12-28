import requests 

import json
import base64

request_json = {
    "origin": {"city_code": "JFK", "country": "US"},
    "destination": {"city_code": "LHR", "country": "GB"},
    "departure_date": "2026-01-15",
    "return_date": "2026-01-25",
    "passengers": 2,
    "cabin_class": "economy",
    "preferences": ["non_stop", "window_seat"],
    "max_results": 10,
    "max_price": 1500.0,
    "max_stops": 1
}

json_str = json.dumps(request_json)
b64_encoded =  "ewogICJvcmlnaW4iOiB7CiAgICAiY2l0eSI6ICJOZXcgWW9yayIsCiAgICAiY291bnRyeSI6ICJVU0EiLAogICAgImFpcnBvcnRfY29kZSI6ICJKRksiLAogICAgImxhdGl0dWRlIjogNDAuNjQxMywKICAgICJsb25naXR1ZGUiOiAtNzMuNzc4MQogIH0sCiAgImRlc3RpbmF0aW9uIjogewogICAgImNpdHkiOiAiTG9uZG9uIiwKICAgICJjb3VudHJ5IjogIlVLIiwKICAgICJhaXJwb3J0X2NvZGUiOiAiTEhSIiwKICAgICJsYXRpdHVkZSI6IDUxLjQ3MDAsCiAgICAibG9uZ2l0dWRlIjogLTAuNDU0MwogIH0sCiAgImRlcGFydHVyZV9kYXRlIjogIjIwMjYtMDYtMDEiLAogICJyZXR1cm5fZGF0ZSI6ICIyMDI2LTA2LTE1IiwKICAicGFzc2VuZ2VycyI6IDEsCiAgImNhYmluX2NsYXNzIjogImJ1c2luZXNzIiwKICAicHJlZmVyZW5jZXMiOiBbIkxVWFVSWSIsICJDSVRZIl0sCiAgIm1heF9yZXN1bHRzIjogMTAsCiAgIm1heF9wcmljZSI6IDI1MDAuMCwKICAibWF4X3N0b3BzIjogMAp9"
#print(b64_encoded)

response = requests.get(
    f"http://127.0.0.1:8000/get_flight_data/?query={b64_encoded}&list_size=1"
)
print(response.text)
decoded_str = base64.b64decode(response.text).decode('utf-8')

