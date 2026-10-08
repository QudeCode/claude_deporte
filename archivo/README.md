# Archivo

Copia íntegra de la carpeta Deporte de Google Drive, descargada el 08/10/2026 con el conector de Drive. Solo consulta: los documentos vivos están en la raíz del repo. En Drive no se ha borrado nada.

Los archivos binarios coinciden byte a byte en tamaño con Drive. Los marcados como *exportado* eran Google Docs o Sheets y se han exportado al formato indicado.

## Raíz

- `registro_maestro_final_2026-10-08.xlsx` — «Registro maestro» de Drive en su estado final, *exportado* a xlsx (Panel, LEEME, fórmulas y gráficos). Origen: `Deporte/Registro maestro`.
- `Registro maestro.xlsx` — versión del registro anterior al paso a Google Sheets (01/10/2026). Origen: `Deporte/Archivo/`.
- `2026-S40_plan_v4.pdf` — plan de la S40 en PDF (versión 4), antes de pasar a Google Docs. Origen: `Deporte/Archivo/`.
- `manual_v1.pdf` — manual v1 en PDF. Origen: `Deporte/Archivo/`.

## semanas/2026-S39/

Origen: `Deporte/Semanas/2026-S39/`.

- `2026-S39_plan.pdf` — plan de la semana 2026-S39.
- `2026-S39_revision.pdf` — revisión de la semana 2026-S39.
- `estado_2026-09-27.pdf` — estado general a 27/09/2026 (antecesor del Panel).

## docs_drive/

Google Docs vivos en el momento de la migración, *exportados* a PDF como copia fiel del formato. Su versión en Markdown está en la raíz del repo.

- `perfil_del_atleta.pdf` — `Deporte/Perfil del atleta` (v4) → `perfil.md`.
- `manual.pdf` — `Deporte/Manual` (v2) → `manual.md`.
- `2026-S41_plan.pdf` — `Deporte/2026-S41 · Plan` → `semanas/2026-S41/plan.md`.
- `2026-S40_plan.pdf` — `Deporte/Semanas/2026-S40/2026-S40 · Plan` → `semanas/2026-S40/plan.md`.
- `2026-S40_revision.pdf` — `Deporte/Semanas/2026-S40/2026-S40 · Revisión` → `semanas/2026-S40/revision.md`.

## old/

Primeras versiones del sistema (13/09/2026). Origen: `Deporte/Archivo/old/`.

- `Deporte.xlsx` — primer libro de Excel (hojas «Objetivos Marzo» y «Rutina Gym Marzo»).
- `deporte_it2.xlsx` — segunda iteración en Google Sheets, *exportada* a xlsx.
- `Deporte.htm` — `Deporte.xlsx` guardado como página web desde Excel; necesita la carpeta `Deporte_archivos/`.
- `Deporte_tmp.htm` — versión temporal de la página web anterior; necesita `Deporte_tmp_archivos/`.
- `Deporte_archivos/` — recursos de `Deporte.htm`: `sheet001.htm` y `sheet002.htm` (las dos hojas), `image001.png` a `image005.png`, `stylesheet.css`, `tabstrip.htm` (pestañas) y `filelist.xml`.
- `Deporte_tmp_archivos/` — recursos de `Deporte_tmp.htm`: `sheet001.htm`, `image001.png`, `image002.png`, `stylesheet.css`, `tabstrip.htm` y `filelist.xml`.
