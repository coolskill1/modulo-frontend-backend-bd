import { supabase } from "./supabase";
import { useState } from "react";
import "./App.css";

export default function App() {
  const [usuario, setUsuario] = useState(null); // null = no logueado
  const [menuAbierto, setMenuAbierto] = useState(false);
  const [loginAbierto, setLoginAbierto] = useState(false);
  const [seccion, setSeccion] = useState("inicio"); // inicio | documentos | reportes
  const [rut, setRut] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  
  
  const formatearRut = (valor) => {
    const limpio = valor.replace(/[^0-9kK]/g, "").toUpperCase();
    if (limpio.length <= 1) return limpio;
    return `${limpio.slice(0, -1)}-${limpio.slice(-1)}`;
  };

  const validarRut = (valor) => {
    const limpio = valor.replace(/[^0-9kK]/g, "").toUpperCase();
    if (limpio.length < 2) return false;
    const cuerpo = limpio.slice(0, -1);
    const dv = limpio.slice(-1);

    let suma = 0;
    let multiplo = 2;
    for (let i = cuerpo.length - 1; i >= 0; i--) {
      suma += parseInt(cuerpo[i], 10) * multiplo;
      multiplo = multiplo === 7 ? 2 : multiplo + 1;
    }
    const resto = 11 - (suma % 11);
    const dvEsperado = resto === 11 ? "0" : resto === 10 ? "K" : String(resto);
    return dv === dvEsperado;
  };

  const handleLogin = async (e) => {
  e.preventDefault();
  setError("");

  if (!validarRut(rut)) {
    setError("El RUT ingresado no es válido.");
    return;
  }

  const { data, error } = await supabase
    
    .from("usuarios")
    .select("id, rut, nombre")
    .eq("rut", rut)
    .eq("password", password)
    .maybeSingle();
    console.log("RUT enviado:", JSON.stringify(rut));
    console.log("Respuesta:", { data, error });

  if (error) {
    setError("Error al conectar con la base de datos.");
    console.error(error);
    return;
  }

  if (!data) {
    setError("RUT o contraseña incorrectos.");
    return;
  }

  setUsuario(data);
  setSeccion("inicio");
  setLoginAbierto(false);
  setRut("");
  setPassword("");
};

  const cerrarSesion = () => {
    setUsuario(null);
    setMenuAbierto(false);
    setSeccion("inicio");
  };

  const irA = (nueva) => {
    setSeccion(nueva);
    setMenuAbierto(false);
  };

  const subirImagen = async (archivo) => {
  setCargando(true);
  const form = new FormData();
  form.append("imagen", archivo);
  form.append("usuario_id", usuario.id);

  try {
    const res = await fetch("http://localhost:8000/api/documentos/imagen", {
      method: "POST",
      body: form,
    });
    const json = await res.json();
    if (!res.ok) {
      alert(json.detail);
      return;
    }
    alert("Documento guardado");

  } catch (err) {
    alert("No se pudo conectar con el servidor.");
  } finally {
    setCargando(false);
  }
};

  return (
    <div className="app">
      <header className="navbar">
        {usuario ? (
          <button
            className="burger"
            onClick={() => setMenuAbierto(!menuAbierto)}
            aria-label="Abrir menú"
            aria-expanded={menuAbierto}
          >
            <span />
            <span />
            <span />
          </button>
        ) : (
          <button className="btn-login" onClick={() => setLoginAbierto(true)}>
            Login
          </button>
        )}

        {usuario && (
          <button className="btn-salir" onClick={cerrarSesion}>
            Salir
          </button>
        )}
      </header>

      {/* Menú lateral: solo existe con sesión iniciada */}
      {usuario && (
        <>
          <aside className={`sidebar ${menuAbierto ? "abierto" : ""}`}>
            <nav>
              <button
                className={seccion === "documentos" ? "activo" : ""}
                onClick={() => irA("documentos")}
              >
                Ingresar documentos
              </button>
              <button
                className={seccion === "reportes" ? "activo" : ""}
                onClick={() => irA("reportes")}
              >
                Reportes
              </button>
            </nav>
          </aside>
          {menuAbierto && (
            <div className="overlay" onClick={() => setMenuAbierto(false)} />
          )}
        </>
      )}

      <main className="contenido">
        {!usuario && (
          <>
            <h1>Bienvenido</h1>
            <p>Inicia sesión para continuar.</p>
          </>
        )}

        {usuario && seccion === "inicio" && (
          <>
            <h1>Hola, {usuario.nombre}</h1>
            <p>Usa el menú para navegar.</p>
          </>
        )}

        {usuario && seccion === "documentos" && (
          <>
            <h1>Ingresar documentos</h1>
            <input
              type="file"
              accept="image/*"
              disabled={cargando}
              onChange={(e) => e.target.files[0] && subirImagen(e.target.files[0])}
            />
            {cargando && <p>Procesando la boleta, esto puede tardar...</p>}
          </>
        )}

        {usuario && seccion === "reportes" && (
          <>
            <h1>Reportes</h1>
            <p>Aquí va el listado de reportes.</p>
          </>
        )}
      </main>

      {loginAbierto && (
        <div className="modal-fondo" onClick={() => setLoginAbierto(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Iniciar sesión</h2>
            <form onSubmit={handleLogin}>
              <label>
                RUT
                <input
                  type="text"
                  placeholder="12.345.678-9"
                  value={rut}
                  onChange={(e) => setRut(formatearRut(e.target.value))}
                  maxLength={10}
                  required
                />
              </label>

              <label>
                Contraseña
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </label>

              {error && <p className="error">{error}</p>}

              <button type="submit" className="btn-enviar">
                Ingresar
              </button>
            </form>
            <button className="cerrar" onClick={() => setLoginAbierto(false)}>
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  );
}