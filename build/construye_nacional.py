"""Arma data/nacional.json y site/index.html. Corre en el equipo de Rodrigo; sólo lee otros proyectos y escribe en este repositorio.

Toma sólo agregados por ciudad de la consulta `2026-11_columna-perimetros-datos`, medidos con un mismo método. No lee patentes ni coordenadas individuales:
la posición de cada ciudad es el centroide ponderado por población de sus manzanas, a una décima de kilómetro.

Uso: python -X utf8 build/construye_nacional.py
"""
import json, math, os, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
RMG = Path.home() / "Análisis RMG"
CONS = RMG / "Datos transporte público gran ccp" / "consultas" / "2026-11_columna-perimetros-datos"
sys.path.insert(0, str(CONS))
import comun as K

REPO = Path(__file__).resolve().parent.parent
V = K.lee(K.DATOS / "velocidad_comparada.json")
N = K.lee(K.DATOS / "cobertura_nse.json")
O = K.lee(K.DATOS / "oferta_demanda_horario.json")
BK = {c: v["LIVE_BUCKET"] for c, v in K.lee(K.REG / "_deploy_capture_multi" / "cities.json").items()}
BK.update({"temuco": "temuco-transporte-live", "punta_arenas": "puntaarenas-transporte-live", "gccp": "gccp-transporte-live"})


def centroide(c):
    x = K.lee(K.data(c) / "cobertura.json")
    s, sx, sy = 0, 0.0, 0.0
    for f in x["features"]:
        p = f["properties"]
        n = p.get("n") or 0
        if n and p.get("cx") is not None:
            s += n
            sx += p["cx"] * n
            sy += p["cy"] * n
    return round(sy / s, 3), round(sx / s, 3)


ciudades = []
for c in K.CIUDADES:
    la, lo = centroide(c)
    h = O[c]["buses_por_hora"]
    pico = max(max(h[6:10]), max(h[16:21]))
    b = K.lee(K.data(c) / "baseline_30min.json")
    ciudades.append({"id": c, "nombre": K.NOMBRE[c], "lat": la, "lon": lo, "parcial": c in K.PARCIALES, "pob": N[c]["pob"], "vivo": c in BK,
                     "vel_lab": round(V[c]["L60"], 1), "vel_dom": round(V[c]["D60"], 1), "gana_dom": round(100 * (V[c]["ganancia_D"] - 1)), "cob400": N[c]["pct_cub_publicado"],
                     "horas": O[c]["horario"]["horas_50"], "hasta": O[c]["horario"]["hasta_50"], "buses_pico": round(pico), "buses_10k": round(1e4 * pico / N[c]["pob"], 1),
                     "pct_22": round(O[c]["horario"]["pct_punta_22"]), "valle": round(O[c]["oferta_buses"]["valle_pct"]),
                     "normal": {t: [round(x) if x is not None else None for x in b[t]["buses_op"]] for t in "LSD"}})
ciudades.sort(key=lambda x: -x["lat"])
os.makedirs(REPO / "site" / "data", exist_ok=True)
nacional = {"ciudades": ciudades, "buckets": {c: BK[c] for c in BK}, "muestra": "marzo, mayo, junio y julio de 2026"}
with open(REPO / "scripts" / "buckets.json", "w", encoding="utf-8") as f:
    json.dump(BK, f, ensure_ascii=False, indent=1)
vitrina = {k: v for k, v in nacional.items() if k != "buckets"}
tpl = (REPO / "build" / "index.template.html").read_text(encoding="utf-8")
LF = RMG / "Tablero nacional transporte" / "_tmp"
html = (tpl.replace("/*__LEAFLET_CSS__*/", (LF / "leaflet.css").read_text(encoding="utf-8"))
           .replace("/*__LEAFLET_JS__*/", (LF / "leaflet.js").read_text(encoding="utf-8"))
           .replace("/*__NACIONAL__*/null", json.dumps(vitrina, ensure_ascii=False, separators=(",", ":"))))
with open(REPO / "site" / "index.html.tmp", "w", encoding="utf-8") as f:
    f.write(html)
os.replace(REPO / "site" / "index.html.tmp", REPO / "site" / "index.html")
print("ciudades", len(ciudades), "html KB", round(len(html.encode()) / 1024), "orden", [c["id"] for c in ciudades][:5])
