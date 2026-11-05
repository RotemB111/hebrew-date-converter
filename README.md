# Hebrew Date Converter

A simple web service and page that converts a Gregorian date to a Hebrew date, using the [Hebcal Hebrew Date Converter REST API](https://www.hebcal.com/home/219/hebrew-date-converter-rest-api).

## How it works

```
Browser (public/index.html)  -->  Python server (app.py)  -->  Hebcal API
        date picker                GET /api/convert             /converter?cfg=json&date=...&g2h=1
```

1. The user picks a date on the page and clicks **Convert**.
2. The page calls our own endpoint: `GET /api/convert?date=YYYY-MM-DD&afterSunset=false`.
3. The server (Python + Flask) checks the input, calls Hebcal, and returns a short JSON result.
4. The page shows the Hebrew date, its English spelling, and any events (holidays, Torah portion).

## Running it

Requirements: Python 3.9 or newer.

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:3000

On Windows, if `python` doesn't work, use `py -m pip install -r requirements.txt` and `py app.py`.

## Deploying online (Render.com, free)

The repo includes a [render.yaml](render.yaml) file:

1. Sign in to https://render.com with GitHub.
2. Click **New → Blueprint** and choose this repository.
3. Render installs the requirements and starts the server with `gunicorn app:app`.

## API

`GET /api/convert?date=2026-11-05`

```json
{
  "gregorian": "2026-11-05",
  "hebrew": "כ״ה בְּחֶשְׁוָן תשפ״ז",
  "english": "25 Cheshvan 5787",
  "events": ["Parashat Chayei Sara"]
}
```

| Parameter     | Required | Description                                             |
|---------------|----------|---------------------------------------------------------|
| `date`        | yes      | Gregorian date, `YYYY-MM-DD`                            |
| `afterSunset` | no       | `true` if the time is after sunset (Hebrew day starts at sunset) |

Errors return a JSON `{ "error": "..." }` with status `400` (bad input) or `502` (Hebcal is unavailable).

> Notes:
> - The server calls Hebcal as in the docs: `https://www.hebcal.com/converter?cfg=json&date=YYYY-MM-DD&g2h=1`. Because Hebcal silently rolls invalid dates forward (e.g. Feb 30 becomes Mar 2), the server checks that the date really exists before calling Hebcal.
> - Calls to Hebcal have a 10 second timeout and are retried once on a network error.

## Credit

Hebrew date data is provided by [Hebcal.com](https://www.hebcal.com/) under the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license.
