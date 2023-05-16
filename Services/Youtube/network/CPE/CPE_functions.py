import requests
import traceback
def resetCPE():
    base = "http://127.0.0.1:6000"
    header = {'content-type': 'application/json'}
    url = "/CPE/-1"
    d = dict()

    try:
        r = requests.get(base + url, timeout=5, headers=header)
        return r.json()
    except:
        traceback.print_exc()
        print("REST unavailable")
        return {}