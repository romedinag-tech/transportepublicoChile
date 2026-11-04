"""Resume el dato en vivo de cada ciudad en site/data/vivo.json. Corre en GitHub Actions cada 30 minutos.

Lee el dia.json público de cada ciudad y conserva sólo cifras de sistema: buses en ruta, hora de la captura, tipo de día y franja.
Así el visitante nunca golpea los buckets: el gasto no crece con las visitas.
"""
import datetime, json, os, sys, time, urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).resolve().parent
BK = json.loads((AQ / "buckets.json").read_text(encoding="utf-8"))
sal = {}
for c, b in sorted(BK.items()):
    try:
        req = urllib.request.Request(f"https://storage.googleapis.com/{b}/dia.json?nc={int(time.time())}", headers={"Cache-Control": "no-cache"})
        d = json.loads(urllib.request.urlopen(req, timeout=40).read())
        sal[c] = {"snapshot": d.get("snapshot"), "fecha": d.get("fecha"), "tipo": d.get("dia_tipo"), "bin": d.get("bin"), "buses": d.get("buses_op")}
    except Exception as e:
        print("sin dato", c, type(e).__name__, flush=True)
        sal[c] = None
out = AQ.parent / "site" / "data"
os.makedirs(out, exist_ok=True)
with open(out / "vivo.json.tmp", "w", encoding="utf-8") as f:
    json.dump({"generado": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "ciudades": sal}, f, ensure_ascii=False, separators=(",", ":"))
os.replace(out / "vivo.json.tmp", out / "vivo.json")
ok = [v for v in sal.values() if v]
print("ciudades con dato", len(ok), "de", len(sal), "buses", sum((v["buses"] or 0) for v in ok))
