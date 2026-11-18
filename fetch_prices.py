import json
from datetime import datetime, time, timedelta
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from zoneinfo import ZoneInfo

zone = ZoneInfo("Europe/Zurich")
today = datetime.now(zone).date()
for offset in (0, 1):
    day = today + timedelta(days=offset)
    start = datetime.combine(day, time.min, zone)
    end = start + timedelta(days=1)
    query = urlencode({"start_timestamp": start.isoformat(), "end_timestamp": end.isoformat()})
    url = "https://api.tariffs.groupe-e.ch/v2/tariffs?" + query
    try:
        with urlopen(url, timeout=30) as response:
            payload = json.load(response)
        rows = payload["prices"] if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            raise ValueError("Format de réponse inattendu")
        rows = [row for row in rows if start <= datetime.fromisoformat(row["start_timestamp"]) < end]
        if not rows and offset == 0:
            raise ValueError("Aucun tarif pour aujourd’hui")
    except Exception as error:
        if offset == 0:
            raise
        print(f"Tarifs de demain indisponibles ({error})")
        rows = []
    Path(f"site/{day}.json").write_text(json.dumps(rows), encoding="utf-8")
