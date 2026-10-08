"""Calcula el estado general a partir de datos/ (sustituye al Panel y al Resumen_semanal).

Uso:
    python3 scripts/resumen.py                 # regenera estado.md
    python3 scripts/resumen.py --semana 2026-S41   # imprime el resumen de una semana (para el cierre)
"""
import csv
import datetime as dt
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"
INICIO_SISTEMA = "2026-S39"


def leer(nombre):
    with open(DATOS / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def fmt(x, dec=1):
    s = f"{x:.{dec}f}".rstrip("0").rstrip(".") if isinstance(x, float) else str(x)
    return s.replace(".", ",")


def ritmo(segundos, km):
    if not km:
        return "—"
    s = round(segundos / km)
    return f"{s // 60}:{s % 60:02d}"


def semana_iso(fecha):
    a, s, _ = dt.date.fromisoformat(fecha).isocalendar()
    return f"{a}-S{s:02d}"


def resumen_semanas():
    """Totales por semana: misma lógica que la antigua pestaña Resumen_semanal."""
    sem = defaultdict(lambda: defaultdict(float))
    for r in leer("sesiones.csv"):
        w = sem[r["Semana"]]
        if r["Disciplina"] == "Fuerza" and r["Estado"] != "No hecha":
            w["fuerza"] += 1
        if r["Estado"] == "No hecha":
            w["no_hechas"] += 1
    for r in leer("series_fuerza.csv"):
        if r["Patrón"] == "Tirón horizontal":
            sem[r["Semana"]]["tiron"] += 1
        elif r["Patrón"] == "Empuje horizontal":
            sem[r["Semana"]]["empuje"] += 1
    for r in leer("carreras.csv"):
        w = sem[r["Semana"]]
        w["carreras"] += 1
        w["km"] += num(r["Distancia (km)"])
        w["seg"] += num(r["Tiempo (s)"])
    return sem


def fila_semana(nombre, w):
    t, e = int(w["tiron"]), int(w["empuje"])
    regla = "cumple" if t >= e else "**no cumple**"
    return (f"| {nombre} | {int(w['fuerza'])} · {int(w['carreras'])} | {t} : {e} · {regla} "
            f"| {fmt(w['km'], 2)} km · {round(w['seg'] / 60)} min | {int(w['no_hechas'])} |")


CAB_SEMANAS = ["| Semana | Sesiones fuerza · carrera | Tirón : empuje horizontal | Carrera | No hechas |",
               "|---|---|---|---|---|"]


def marcas():
    maximos = defaultdict(lambda: {"reps": 0.0, "peso": 0.0, "ultimo": ""})
    for r in leer("series_fuerza.csv"):
        m = maximos[r["Ejercicio"]]
        m["reps"] = max(m["reps"], num(r["Reps"]))
        m["peso"] = max(m["peso"], num(r["Peso (kg)"]))
        m["ultimo"] = max(m["ultimo"], r["Fecha"])
    out = ["| Ejercicio | Referencia actual verificada | Máx. reps | Máx. peso | Último |", "|---|---|---|---|---|"]
    for r in leer("marcas.csv"):
        m = maximos.get(r["Ejercicio"], {"reps": 0, "peso": 0, "ultimo": "—"})
        carga = f"{fmt(m['peso'])} kg" if m["peso"] else "—"
        out.append(f"| {r['Ejercicio']} | {r['Referencia actual verificada']} | {fmt(m['reps'])} "
                   f"| {carga} | {m['ultimo']} |")
    return out


def dominadas(n=8):
    por_dia = defaultdict(list)
    for r in leer("series_fuerza.csv"):
        if r["Ejercicio"] == "Dominadas":
            por_dia[r["Fecha"]].append(int(num(r["Reps"])))
    out = ["| Fecha | Series | Máx. | Total |", "|---|---|---|---|"]
    for fecha in sorted(por_dia)[-n:]:
        reps = por_dia[fecha]
        out.append(f"| {fecha} | {'-'.join(map(str, reps))} | {max(reps)} | {sum(reps)} |")
    return out


def carreras(n=6):
    out = ["| Fecha | Sesión | Km | Tiempo | Ritmo | FC media | Cadencia |", "|---|---|---|---|---|---|---|"]
    for r in leer("carreras.csv")[-n:]:
        s, km = num(r["Tiempo (s)"]), num(r["Distancia (km)"])
        out.append(f"| {r['Fecha']} | {r['Sesión (Garmin)']} | {fmt(km, 2)} | {int(s // 60)}:{int(s % 60):02d} "
                   f"| {ritmo(s, km)} | {r['FC media']} | {r['Cadencia media (ppm)']} |")
    return out


def peso():
    pesos = [r for r in leer("corporal.csv") if r["Medida"] == "Peso"]
    if not pesos:
        return "—"
    u = max(pesos, key=lambda r: r["Fecha"])
    return f"{fmt(num(u['Valor']))} {u['Unidad']} ({u['Fecha']})"


def estado():
    sem = resumen_semanas()
    ultima = max(r["Fecha"] for r in leer("sesiones.csv") if r["Estado"] != "No hecha")
    semanas = sorted(s for s in sem if s >= INICIO_SISTEMA and any(sem[s].values()))
    lineas = [
        "# Estado general",
        "",
        f"Generado por `scripts/resumen.py`, no se edita a mano. Última sesión registrada: {ultima}. "
        f"Último peso: {peso()}.",
        "",
        "## Objetivos",
        "",
        "| Objetivo | Estado | Siguiente hito |",
        "|---|---|---|",
        *[f"| {r['Objetivo']} | {r['Estado']} | {r['Siguiente hito']} |" for r in leer("objetivos.csv")],
        "",
        "## Semanas",
        "",
        "Regla: series de tirón horizontal ≥ empuje horizontal.",
        "",
        *CAB_SEMANAS,
        *[fila_semana(s, sem[s]) for s in semanas],
        "",
        "## Marcas",
        "",
        *marcas(),
        "",
        "## Dominadas por sesión",
        "",
        *dominadas(),
        "",
        "## Últimas carreras",
        "",
        *carreras(),
        "",
    ]
    (RAIZ / "estado.md").write_text("\n".join(lineas), encoding="utf-8")
    print("estado.md actualizado")


def una_semana(nombre):
    sem = resumen_semanas()
    print("\n".join([*CAB_SEMANAS, fila_semana(nombre, sem[nombre])]))
    print()
    print("| Fecha | Disciplina | Sesión | Estado | Sensación / esfuerzo |")
    print("|---|---|---|---|---|")
    for r in leer("sesiones.csv"):
        if r["Semana"] == nombre:
            print(f"| {r['Fecha']} | {r['Disciplina']} | {r['Sesión']} | {r['Estado']} | {r['Sensación / esfuerzo']} |")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--semana":
        una_semana(sys.argv[2])
    elif len(sys.argv) == 1:
        estado()
    else:
        sys.exit(__doc__)
