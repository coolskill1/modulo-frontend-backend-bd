import json
from pathlib import Path


def json_a_markdown(ruta_json, carpeta_salida):
    carpeta_salida = Path(carpeta_salida)
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    with open(ruta_json, "r", encoding="utf-8") as f:
        documentos = json.load(f)

    rutas_md = []

    for documento in documentos:
        archivo = documento["archivo"]
        textos = documento["textos"]
        cajas = documento["cajas"]

        if len(textos) != len(cajas):
            print(f"Error en {archivo}: textos y cajas no coinciden")
            continue

        lineas = []
        for texto, caja in zip(textos, cajas):
            x_min = min(p[0] for p in caja)
            y_min = min(p[1] for p in caja)
            x_max = max(p[0] for p in caja)
            y_max = max(p[1] for p in caja)
            lineas.append(f"{texto} | {x_min},{y_min},{x_max},{y_max}")

        ruta_md = carpeta_salida / f"{Path(archivo).stem}.md"
        ruta_md.write_text("\n".join(lineas), encoding="utf-8")
        rutas_md.append(ruta_md)

    return rutas_md