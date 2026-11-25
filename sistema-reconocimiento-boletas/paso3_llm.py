import json
import os
import re
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL")

class LLMClient:

    def __init__(self):
        if not API_KEY or not MODEL:
            raise ValueError(
                "Faltan OPENROUTER_API_KEY u OPENROUTER_MODEL en el .env"
            )
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=API_KEY
        )

    def consultar(self, prompt):
        respuesta = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente experto en extracción "
                        "de información de facturas."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        if not respuesta.choices:
            raise ValueError("OpenRouter no devolvió ninguna respuesta.")

        mensaje = respuesta.choices[0].message

        if mensaje.content is None:
            raise ValueError(
                f"El modelo no devolvió texto. "
                f"Finish reason: {respuesta.choices[0].finish_reason}."
            )

        return mensaje.content


def extraer_informacion(llm, ruta_documento):
    with open(ruta_documento, "r", encoding="utf-8") as archivo:
        contenido = archivo.read()

    prompt = f"""
    Analiza el siguiente documento de factura.

    El documento está representado en formato Markdown.
    Cada línea contiene texto reconocido mediante OCR,
    seguido de sus coordenadas en el documento.

    Extrae los siguientes datos:

    - rut_comprador
    - nombre_comprador
    - rut_vendedor
    - empresa_vendedora
    - numero_documento
    - fecha_compra
    - monto_comprado

    Consideraciones:

    - El comprador corresponde al receptor.
    - El vendedor corresponde al emisor.
    - El monto debe ser el total final de la factura.
    - La fecha debe estar en formato YYYY-MM-DD.
    - No inventes información.
    - Si no encuentras un dato, devuelve null.
    - Si existen datos contradictorios, devuelve null
      para ese campo.
    - Utiliza las coordenadas para interpretar la
      distribución espacial de los elementos.
    - Considera posibles errores de reconocimiento OCR.

    Devuelve exclusivamente un JSON válido con los campos solicitados.

    Documento Markdown:

    {contenido}
    """

    respuesta = llm.consultar(prompt).strip()
    respuesta = re.sub(r"^```(?:json)?\s*", "", respuesta)
    respuesta = re.sub(r"\s*```$", "", respuesta)

    try:
        return json.loads(respuesta)
    except json.JSONDecodeError:
        print("El modelo no devolvió un JSON válido. Respuesta recibida:")
        print(respuesta)
        raise

def main():
    if len(sys.argv) < 2:
        raise SystemExit("Uso: python paso3_llm.py ruta/al/documento.md")

    ruta = sys.argv[1]
    resultado = extraer_informacion(LLMClient(), ruta)

    salida = os.path.splitext(ruta)[0] + "_resultado.json"
    with open(salida, "w", encoding="utf-8") as archivo:
        json.dump(resultado, archivo, ensure_ascii=False, indent=2)

    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    print(f"\nJSON guardado en: {salida}")

if __name__ == "__main__":
    main()