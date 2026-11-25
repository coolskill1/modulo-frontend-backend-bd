import json
import sys
from pathlib import Path

from paso1_ocr import ejecutar_ocr
from paso2_markdown import json_a_markdown
from paso3_llm import LLMClient, extraer_informacion


def procesar_factura(ruta_imagen, carpeta_salida="salida"):
    base = Path(carpeta_salida)
    base.mkdir(exist_ok=True)
    ruta_json = base / f"{Path(ruta_imagen).stem}.json"

    print("[1/3] OCR...")
    ejecutar_ocr(ruta_imagen, ruta_json)

    print("[2/3] Markdown...")
    rutas_md = json_a_markdown(ruta_json, base)

    print("[3/3] Consulta al modelo...")
    llm = LLMClient()
    return [extraer_informacion(llm, md) for md in rutas_md]


if __name__ == "__main__":
    for resultado in procesar_factura(sys.argv[1]):
        print(json.dumps(resultado, ensure_ascii=False, indent=4))