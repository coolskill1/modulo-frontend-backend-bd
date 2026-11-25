import os
import re
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client

from pipeline import procesar_factura

load_dotenv()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SECRET_KEY"],
)

try:
    respuesta = supabase.table("documentos").select("*").limit(1).execute()

    print("Consulta realizada correctamente")
    print(respuesta.data)

except Exception as e:
    print("Error consultando Supabase:")
    print(type(e).__name__, str(e))


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalizar_rut(valor):
    # Deja el RUT como XXXXXXXX-D, igual que en la tabla usuarios
    if not valor:
        return None
    limpio = re.sub(r"[^0-9kK]", "", str(valor)).upper()
    if len(limpio) < 2:
        return None
    return f"{limpio[:-1]}-{limpio[-1]}"


def normalizar_monto(valor):
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return int(valor)
    digitos = re.sub(r"[^0-9]", "", str(valor))
    return int(digitos) if digitos else None


def normalizar_fecha(valor):
    if not valor:
        return None
    try:
        return datetime.strptime(str(valor), "%Y-%m-%d").date().isoformat()
    except ValueError:
        return None


@app.post("/api/documentos/imagen")
def procesar_imagen(imagen: UploadFile = File(...), usuario_id: int = Form(...)):
    if not imagen.content_type or not imagen.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen.")

    extension = Path(imagen.filename or "").suffix or ".jpg"

    # Guardamos la imagen en una carpeta temporal con nombre único
    # para no mezclar archivos entre usuarios
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = Path(carpeta) / f"{uuid.uuid4().hex}{extension}"
        with open(ruta, "wb") as destino:
            shutil.copyfileobj(imagen.file, destino)

        try:
            resultados = procesar_factura(str(ruta), carpeta_salida=carpeta)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {e}")

    if not resultados:
        raise HTTPException(status_code=422, detail="No se pudo extraer información del documento.")

    extraido = resultados[0]
    fila = {
        "usuario_id": usuario_id,
        "rut_comprador": normalizar_rut(extraido.get("rut_comprador")),
        "nombre_comprador": extraido.get("nombre_comprador"),
        "rut_vendedor": normalizar_rut(extraido.get("rut_vendedor")),
        "empresa_vendedora": extraido.get("empresa_vendedora"),
        "numero_documento": extraido.get("numero_documento"),
        "fecha_compra": normalizar_fecha(extraido.get("fecha_compra")),
        "monto_comprado": normalizar_monto(extraido.get("monto_comprado")),
    }

    respuesta = supabase.table("documentos").insert(fila).execute()
    return {"ok": True, "documento": respuesta.data[0]}