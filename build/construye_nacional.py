"""Arma site/index.html y scripts/buckets.json. Corre en el equipo de Rodrigo; sólo lee otros proyectos y escribe en este repositorio.

Toma sólo agregados por ciudad de la consulta `2026-11_columna-perimetros-datos`. No lee patentes ni coordenadas individuales: la posición de cada ciudad
es el centroide ponderado por población de sus manzanas.

Reglas de comparación, declaradas en la página:
- Cobertura y buses por habitante: sin las comunas con menos de 60 % de su población a 400 m de un paradero, medidas en `17_revisa_perimetros.py`.
- Gran Concepción: los buses por hora del histórico cubren 36 líneas y 7 comunas, así que buses por habitante usa esas 7 comunas.
- Sistemas de menos de 5 líneas: aparte, fuera del ranking principal. La Serena, parcial, no se compara.

Uso: python -X utf8 build/construye_nacional.py
"""
import json, math, os, statistics as st, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
RMG = Path.home() / "Análisis RMG"
CONS = RMG / "Datos transporte público gran ccp" / "consultas" / "2026-11_columna-perimetros-datos"
sys.path.insert(0, str(CONS))
sys.path.insert(0, str(Path.home() / ".claude" / "skills" / "grafico-interactivo" / "scripts"))
import comun as K
import grafico

REPO = Path(__file__).resolve().parent.parent
V = K.lee(K.DATOS / "velocidad_comparada.json")
O = K.lee(K.DATOS / "oferta_demanda_horario.json")
P = K.lee(K.DATOS / "revision_perimetros.json")
BK = {c: v["LIVE_BUCKET"] for c, v in K.lee(K.REG / "_deploy_capture_multi" / "cities.json").items()}
BK.update({"temuco": "temuco-transporte-live", "punta_arenas": "puntaarenas-transporte-live", "gccp": "gccp-transporte-live"})
BK.pop("linares", None)          # sin captura activa: su último dia.json es del 2026-10-21, con 0 buses
SIETE = {"CONCEPCIÓN", "SAN PEDRO DE LA PAZ", "TALCAHUANO", "HUALPÉN", "CHIGUAYANTE", "PENCO", "HUALQUI"}
T95 = {3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571, 7: 2.447, 8: 2.365}


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


def dia_medio(v, d):
    xs = [v["por_dia"][d][str(b)]["v_60"] for b in range(14, 42) if str(b) in v["por_dia"][d] and v["por_dia"][d][str(b)].get("v_60") is not None]
    return st.mean(xs) if xs else None


def vel_hora(v):
    dias = [d for d, x in v["dias"].items() if x["tipo"] == "L" and x.get("filas")]
    out = []
    for h in range(6, 23):
        xs = []
        for d in dias:
            ys = [v["por_dia"][d][str(b)]["v_60"] for b in (2 * h, 2 * h + 1) if str(b) in v["por_dia"][d] and v["por_dia"][d][str(b)].get("v_60") is not None]
            if ys:
                xs.append(st.mean(ys))
        out.append([h, round(st.mean(xs), 1) if xs else None])
    return out


ciudades, horas_v, formas = [], {}, {}
for c in K.CIUDADES:
    la, lo = centroide(c)
    h = O[c]["buses_por_hora"]
    pico = max(max(h[6:10]), max(h[16:21]))
    b = K.lee(K.data(c) / "baseline_30min.json")
    com = P["por_ciudad"][c]["comunas"]
    sint = P["sintesis"].get(c)
    excl = sorted(sint["bajo_umbral"]) if sint else []
    pob_tot = P["por_ciudad"][c]["pob"]
    pob = sint["pob_sin"] if sint else pob_tot
    cob = sint["pct_cub_sin"] if sint else P["por_ciudad"][c]["pct_cub"]
    den = sum(v["pob"] for k, v in com.items() if k in SIETE) if c == "gccp" else pob
    v = K.lee(K.DATOS / "vel" / f"{c}.json")
    dl = [dia_medio(v, d) for d, x in v["dias"].items() if x["tipo"] == "L" and x.get("filas")]
    dl = [x for x in dl if x is not None]
    ic = T95.get(len(dl) - 1, 2.0) * st.stdev(dl) / math.sqrt(len(dl)) if len(dl) > 2 else None
    lin = V[c]["lineas"]
    grupo = "parcial" if c in K.PARCIALES else ("pequeno" if lin < 5 else "grande")
    horas_v[c] = vel_hora(v)
    formas[c] = [[i, round(100 * h[i] / pico, 1)] for i in range(5, 24)]
    ciudades.append({"id": c, "nombre": K.NOMBRE[c], "lat": la, "lon": lo, "grupo": grupo, "pob": pob, "pob_total": pob_tot, "excl": [x.title() for x in excl], "comunas": [k.title() for k in com if k not in excl],
                     "vivo": c in BK, "lineas": lin, "dias_l": V[c]["dias_L"], "dias_d": V[c]["dias_D"], "pulsos": V[c]["pulsos"],
                     "vel_lab": round(V[c]["L60"], 1), "vel_ic": round(ic, 1) if ic else None, "vel_dom": round(V[c]["D60"], 1), "gana_dom": round(100 * (V[c]["ganancia_D"] - 1)), "cob400": cob,
                     "horas": O[c]["horario"]["horas_50"], "hasta": O[c]["horario"]["hasta_50"], "hasta20": O[c]["horario"]["hasta_20"], "buses_pico": round(pico), "buses_10k": round(1e4 * pico / den, 1),
                     "pct_22": round(O[c]["horario"]["pct_punta_22"]), "valle": round(O[c]["oferta_buses"]["valle_pct"]),
                     "normal": {t: [round(x) if x is not None else None for x in b[t]["buses_op"]] for t in "LSD"}})
ciudades.sort(key=lambda x: -x["lat"])

SERIES = [("santiago", "--gi-s1"), ("valparaiso", "--gi-s3"), ("gccp", "--gi-s2"), ("temuco", "--gi-s6"), ("rancagua", "--gi-s5"), ("calama", "--gi-s4")]
EJE_H = {"min": 5, "max": 23, "paso": 2, "etiqueta": "Hora del día"}
g_forma = {"tipo": "lineas", "id": "forma", "titulo": "Buses en ruta durante un día laboral", "unidad": "% de la punta", "dec": 0, "alto": 400, "ancho": 1300, "x": EJE_H, "y": {"min": 0, "max": 110, "ticks": [0, 25, 50, 75, 100]},
           "series": [{"id": c, "nombre": K.NOMBRE[c], "color": col, "grosor": 2.2, "conmutable": True, "puntos": formas[c]} for c, col in SERIES],
           "hover": {"normal": "todas", "lupa": "cercanas"}, "nota": "Promedio histórico de días laborales, cada ciudad respecto de su propia hora punta. Muestra la forma del día, no la cantidad de buses."}
g_vel = {"tipo": "lineas", "id": "velhora", "titulo": "Velocidad de los buses por hora, día laboral", "unidad": "km/h", "dec": 1, "alto": 400, "ancho": 1300, "x": {"min": 6, "max": 22, "paso": 2, "etiqueta": "Hora del día"}, "y": {"min": 10, "max": 30, "ticks": [10, 15, 20, 25, 30]},
         "series": [{"id": c, "nombre": K.NOMBRE[c], "color": col, "grosor": 2.2, "conmutable": True, "puntos": horas_v[c]} for c, col in SERIES],
         "hover": {"normal": "todas", "lupa": "cercanas"}, "nota": "Velocidad física con un pulso por bus por minuto, sin terminales. Muestra de 8 días laborales de 2026."}
gr = [c for c in ciudades if c["grupo"] == "grande"]
g_disp = {"tipo": "dispersion", "id": "dom", "titulo": "Velocidad en día laboral y aumento en domingo", "unidad": "", "dec": 1, "alto": 420, "ancho": 1300,
          "x": {"etiqueta": "Velocidad en día laboral (km/h)", "min": 12, "max": 22, "ticks": [12, 14, 16, 18, 20, 22]}, "y": {"etiqueta": "Aumento en domingo (%)", "min": 0, "max": 25, "ticks": [0, 5, 10, 15, 20, 25]},
          "color": "--gi-s3", "puntos": [{"x": c["vel_lab"], "y": c["gana_dom"], "nombre": c["nombre"]} for c in gr], "radio": 5, "opacidad": .9,
          "nota": "14 sistemas con 5 líneas o más. Un aumento alto sugiere congestión en día laboral; es un indicio, no una medición de ella. Calculado con 4 domingos."}
g_vistas = {"tipo": "vistas", "id": "porhora", "inicial": "forma", "vistas": [{"id": "forma", "etiqueta": "Forma del día", "grafico": g_forma}, {"id": "velhora", "etiqueta": "Velocidad por hora", "grafico": g_vel}, {"id": "dom", "etiqueta": "Laboral y domingo", "grafico": g_disp}]}
prob = grafico.valida(g_vistas)
assert not prob, prob

os.makedirs(REPO / "site" / "data", exist_ok=True)
os.makedirs(REPO / "scripts", exist_ok=True)
with open(REPO / "scripts" / "buckets.json", "w", encoding="utf-8") as f:
    json.dump(BK, f, ensure_ascii=False, indent=1)
vitrina = {"ciudades": ciudades, "muestra": "marzo, mayo, junio y julio de 2026"}
tpl = (REPO / "build" / "index.template.html").read_text(encoding="utf-8")
LF = RMG / "Tablero nacional transporte" / "_tmp"
sj = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html = (tpl.replace("<!--__GI_ACTIVOS__-->", grafico.activos())
           .replace("/*__LEAFLET_CSS__*/", (LF / "leaflet.css").read_text(encoding="utf-8"))
           .replace("/*__LEAFLET_JS__*/", (LF / "leaflet.js").read_text(encoding="utf-8"))
           .replace("/*__NACIONAL__*/null", sj(vitrina)).replace("/*__GRAF__*/null", sj(g_vistas)))
with open(REPO / "site" / "index.html.tmp", "w", encoding="utf-8") as f:
    f.write(html)
os.replace(REPO / "site" / "index.html.tmp", REPO / "site" / "index.html")
print("ciudades", len(ciudades), "html KB", round(len(html.encode()) / 1024), "grupos", {g: [c["id"] for c in ciudades if c["grupo"] == g] for g in ("pequeno", "parcial")})
print({c["id"]: (c["cob400"], c["buses_10k"], c["vel_ic"], c["excl"]) for c in ciudades if c["excl"]})
