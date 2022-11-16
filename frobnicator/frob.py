import requests

def frobnicate():
    r = requests.get("https://silvair.com")
    return r.text

