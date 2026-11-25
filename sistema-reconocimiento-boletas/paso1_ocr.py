import json
from paddleocr import PaddleOCR

_ocr = None

def _get_ocr():
    global _ocr
    if _ocr is None:
        _ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            enable_mkldnn=False,
            )
    return _ocr


def ejecutar_ocr(ruta_imagen, ruta_json):
    resultados = _get_ocr().predict(str(ruta_imagen))

    salida = []
    for resultado in resultados:
        res = resultado.json["res"]
        salida.append({
            "archivo": str(ruta_imagen),
            "textos": res.get("rec_texts", []),
            "cajas": [
                [[int(x), int(y)] for x, y in caja]
                for caja in res.get("rec_polys", [])
            ],
        })

    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=4)

    return ruta_json