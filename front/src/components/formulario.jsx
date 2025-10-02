import { useState, useRef } from "react";
import axios from "axios";
import Vistas from "../components/vistas";


export default function Formulario() {
  const [direccion, setDireccion] = useState("");
  const [resultado, setResultado] = useState(null);
  const [mensaje, setMensaje] = useState(null);
  const [estado, setEstado] = useState("inicio");
  const [mostrarLoader, setMostrarLoader] = useState(false); 
  const timeoutRef = useRef(null);

  // llamada al backend
  const consultarUbicacion = async (datos) => {
    setResultado(null);
    setMensaje("🔎 Consultando el servicio... por favor espere.");
    setEstado("cargando");

    try {
      const res = await axios.post("http://localhost:4000/consultar_ubicacion", datos);
      mostrarResultadoSegunEstado(res.data);
    } catch (err) {
      setResultado("🚫 Error de conexión. Intentalo más tarde.");
    }

    // timer de inactividad y reinicio
    setTimeout(() => {
      setEstado("resultado");
      timeoutRef.current = setTimeout(() => {
        reiniciarFormulario();
      }, 15000);
    }, 5000);
  };

  const mostrarResultadoSegunEstado = (data) => {
    if (data.tiempo_estimado_llegada) {
      setResultado(data.tiempo_estimado_llegada);
    } else if (data.mensaje) {
      setResultado(data.mensaje);
    } else {
      setResultado("⚠️ No se pudo consultar por el camión más cercano. Intentá otra vez.");
    }
  };

  const enviarDireccion = () => {
    if (direccion.trim()) {
      consultarUbicacion({ direccion });
    } else {
      setResultado("📍 Dirección no válida. Vas a ser redirigido otra vez.");
      setMostrarLoader(true);
      setEstado("resultado");
      timeoutRef.current = setTimeout(() => {
        setMostrarLoader(false);
        reiniciarFormulario();
      }, 5000);
    }
  };

  const reiniciarFormulario = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setDireccion("");
    setResultado(null);
    setMensaje(null);
    setEstado("inicio");
    setMostrarLoader(false);
  };

  return (
    <Vistas
      estado={estado}
      mensaje={mensaje}
      resultado={
        <>
          {resultado}
          {mostrarLoader && <span className="loader"></span>}
        </>
      }
      onReiniciar={reiniciarFormulario}
      childrenInicio={
        <div className="formulario">
          <p>✏️ Ingresá tu dirección (calle y número):</p>
          <input
            className="form"
            type="text"
            placeholder="Ingrese calle y numero:"
            value={direccion}
            onChange={(e) => setDireccion(e.target.value)}
          />
          <button onClick={enviarDireccion} className="btns">
            
            CONSULTAR
          </button>
        </div>
      }
    />
  );
}
