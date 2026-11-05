# Hebrew Date Converter - a small service that converts a Gregorian date
# to a Hebrew date using the Hebcal REST API.
import os
import time
from datetime import datetime

import requests
from flask import Flask, jsonify, request

app = Flask(__name__, static_folder="public", static_url_path="")
app.json.ensure_ascii = False  # show Hebrew letters in the JSON (not כ...)
PORT = int(os.environ.get("PORT", 3000))
HEBCAL_URL = "https://www.hebcal.com/converter"


# Serve the web page (public/index.html)
@app.get("/")
def index():
    return app.send_static_file("index.html")


# GET /api/convert?date=YYYY-MM-DD&afterSunset=true
@app.get("/api/convert")
def convert():
    date = request.args.get("date", "")
    after_sunset = request.args.get("afterSunset") == "true"

    # 1. Validate the input - the date must exist
    #    (Hebcal would silently turn Feb 30 into Mar 2)
    try:
        valid = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d") == date
    except ValueError:
        valid = False
    if not valid:
        return jsonify(error="This date does not exist, please check it"), 400

    # 2. Build the Hebcal request, e.g.
    #    https://www.hebcal.com/converter?cfg=json&date=2011-06-02&g2h=1
    params = {
        "cfg": "json",  # return JSON
        "date": date,   # Gregorian date YYYY-MM-DD
        "g2h": "1",     # convert Gregorian -> Hebrew
    }
    if after_sunset:
        params["gs"] = "on"  # date is after sunset

    try:
        # 3. Call the Hebcal API
        response = get_with_retry(HEBCAL_URL, params)
        data = response.json()
    except (requests.RequestException, ValueError) as err:
        print("Hebcal request failed:", err)
        return jsonify(error="The Hebcal service is unavailable, please try again later"), 502

    if not response.ok or "error" in data:
        return jsonify(error=data.get("error", "Hebcal could not convert this date")), 400

    # 4. Return only the fields the page needs
    return jsonify(
        gregorian=date,
        hebrew=data["hebrew"],                             # e.g. "כ״ה בְּחֶשְׁוָן תשפ״ז"
        english=f"{data['hd']} {data['hm']} {data['hy']}",  # e.g. "25 Cheshvan 5787"
        events=data.get("events", []),                     # e.g. ["Parashat Chayei Sara"]
    )


def get_with_retry(url, params, retries=1):
    """Call an external URL with a 10s timeout, and retry once if the network fails."""
    try:
        return requests.get(url, params=params, timeout=10)
    except (requests.ConnectionError, requests.Timeout) as err:
        if retries == 0:
            raise
        print("Network error, retrying...", err)
        time.sleep(1)  # wait 1 second
        return get_with_retry(url, params, retries - 1)


if __name__ == "__main__":
    print(f"Server running at http://localhost:{PORT}")
    app.run(port=PORT)
