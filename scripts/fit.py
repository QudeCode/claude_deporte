"""Lee un archivo .fit de Garmin y lo pasa a los CSV de datos/.

Uso:
    python3 scripts/fit.py archivo.fit                  # solo muestra lo que se añadiría
    python3 scripts/fit.py archivo.fit --anadir \\
        [--sesion "Colinas"] [--cumplimiento "..."] [--sensacion exigente] [--notas "..."]

Carrera → carreras.csv + carreras_vueltas.csv. Cualquier otro deporte → otras_actividades.csv.
Necesita fitdecode (pip install fitdecode; el hook de inicio de sesión lo instala).
"""
import argparse
import csv
import datetime as dt
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import fitdecode

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"
ZONA = ZoneInfo("Europe/Madrid")
TIPOS = {"warmup": "Calentamiento", "active": "Activo", "interval": "Activo", "rest": "Recuperación",
         "recovery": "Recuperación", "cooldown": "Vuelta a la calma"}


def leer_fit(ruta):
    sesion, vueltas, nombre = None, [], None
    with fitdecode.FitReader(ruta) as fit:
        for frame in fit:
            if frame.frame_type != fitdecode.FIT_FRAME_DATA:
                continue
            g = {f.name: f.value for f in frame.fields}
            if frame.name == "session":
                sesion = g
            elif frame.name == "lap":
                vueltas.append(g)
            elif frame.name == "workout" and g.get("wkt_name"):
                nombre = g["wkt_name"]
    if sesion is None:
        sys.exit("El archivo no tiene mensaje de sesión.")
    return sesion, vueltas, nombre


def cadencia(g, corriendo):
    c = g.get("avg_running_cadence") or g.get("avg_cadence")
    if c is None:
        return ""
    frac = g.get("avg_fractional_cadence") or 0
    # En carrera, Garmin guarda zancadas por minuto (media cadencia): se pasa a pasos por minuto.
    return round((c + frac) * 2) if corriendo else round(c)


def r1(x):
    return "" if x is None else (int(x) if float(x).is_integer() else round(x, 1))


def anadir(nombre, filas):
    ruta = DATOS / nombre
    with open(ruta, encoding="utf-8") as f:
        cab = next(csv.reader(f))
    with open(ruta, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cab, extrasaction="raise", lineterminator="\n")
        for fila in filas:
            w.writerow({k: fila.get(k, "") for k in cab})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fit")
    ap.add_argument("--anadir", action="store_true")
    ap.add_argument("--sesion")
    ap.add_argument("--cumplimiento", default="")
    ap.add_argument("--sensacion", default="")
    ap.add_argument("--notas", default="")
    a = ap.parse_args()

    s, vueltas, nombre_wkt = leer_fit(a.fit)
    inicio = s["start_time"].astimezone(ZONA)
    fecha = inicio.date().isoformat()
    iso = inicio.isocalendar()
    semana = f"{iso[0]}-S{iso[1]:02d}"
    deporte = str(s.get("sport", ""))
    corriendo = deporte == "running"
    fuente = Path(a.fit).name

    for nombre in ("carreras.csv", "otras_actividades.csv"):
        with open(DATOS / nombre, encoding="utf-8") as f:
            if any(r.get("Fuente") == fuente for r in csv.DictReader(f)):
                sys.exit(f"{fuente} ya está en {nombre}.")

    km = round((s.get("total_distance") or 0) / 1000, 2)
    comun = {"Fecha": fecha, "Hora": inicio.strftime("%H:%M"), "Semana": semana, "Distancia (km)": km,
             "FC media": r1(s.get("avg_heart_rate")), "FC máx": r1(s.get("max_heart_rate")),
             "TE aeróbico": r1(s.get("total_training_effect")), "Notas": a.notas, "Fuente": fuente}

    if corriendo:
        fila = {**comun, "Sesión (Garmin)": a.sesion or nombre_wkt or "",
                "Tiempo (s)": round(s.get("total_timer_time") or 0),
                "Cadencia media (ppm)": cadencia(s, True), "Temp (°C)": r1(s.get("avg_temperature")),
                "TE anaeróbico": r1(s.get("total_anaerobic_training_effect")),
                "Cumplimiento": a.cumplimiento, "Sensación": a.sensacion}
        filas_v = [{"Fecha": fecha, "Vuelta": i, "Tipo": TIPOS.get(str(v.get("intensity")), "Activo"),
                    "Distancia (m)": round(v.get("total_distance") or 0),
                    "Tiempo (s)": round(v.get("total_timer_time") or 0, 1),
                    "FC media": r1(v.get("avg_heart_rate")), "FC máx": r1(v.get("max_heart_rate")),
                    "Cadencia (ppm)": cadencia(v, True)}
                   for i, v in enumerate(vueltas, 1)]
        destino = "carreras.csv"
    else:
        fila = {**comun, "Actividad": a.sesion or deporte,
                "Movimiento (s)": round(s.get("total_moving_time") or s.get("total_timer_time") or 0),
                "Total (s)": round(s.get("total_elapsed_time") or 0),
                "Desnivel + (m)": r1(s.get("total_ascent"))}
        filas_v = []
        destino = "otras_actividades.csv"

    seg = fila.get("Tiempo (s)") or fila.get("Movimiento (s)")
    ritmo = f"{int(seg / km) // 60}:{int(seg / km) % 60:02d}/km" if km else "—"
    print(f"{destino}: {fecha} {fila['Hora']} · {deporte} · {fila.get('Sesión (Garmin)') or fila.get('Actividad')}")
    print(f"  {km} km · {seg // 60}:{seg % 60:02d} · {ritmo} · FC {fila['FC media']}/{fila['FC máx']}"
          f" · cadencia {fila.get('Cadencia media (ppm)', '—')} · TE {fila['TE aeróbico']}")
    for v in filas_v:
        print(f"  vuelta {v['Vuelta']}: {v['Tipo']} {v['Distancia (m)']} m en {v['Tiempo (s)']} s"
              f" · FC {v['FC media']}/{v['FC máx']} · cad {v['Cadencia (ppm)']}")

    if a.anadir:
        anadir(destino, [fila])
        if filas_v:
            anadir("carreras_vueltas.csv", filas_v)
        print("Añadido.")
    else:
        print("(vista previa: usa --anadir para guardarlo)")


if __name__ == "__main__":
    main()
