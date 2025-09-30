import { useState, useRef } from "react";
import axios from "axios";
import Vistas from "../components/vistas";

export default function Formulario() {
  const [direccion, setDireccion] = useState("");
  const [resultado, setResultado] = useState(null);
  const [mensaje, setMensaje] = useState(null);
  const [estado, setEstado] = useState("inicio");
  const [mostrarLoader, setMostrarLoader] = useState(false); // 🔹 loader
  const timeoutRef = useRef(null);

  // llamada al backend
  const consultarUbicacion = async (datos) => {
    setResultado(null);
    setMensaje("Consultando servicio... por favor esperá.");
    setEstado("cargando");

    try {
      const res = await axios.post("http://localhost:4000/consultar_ubicacion", datos);
      mostrarResultadoSegunEstado(res.data);
    } catch (err) {
      setResultado("No pudimos conectar con el servidor. Intenta más tarde.");
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
      setResultado("No se pudo obtener información del camión más cercano. Intenta de nuevo.");
    }
  };

  const enviarDireccion = () => {
    if (direccion.trim()) {
      consultarUbicacion({ direccion });
    } else {
      setResultado("Por favor, ingresa una dirección válida! ...Redirigiendo...");
      setMostrarLoader(true); // 🔹 mostrar loader
      setEstado("resultado");
      timeoutRef.current = setTimeout(() => {
        setMostrarLoader(false); // 🔹 ocultar loader
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
          {mostrarLoader && <span className="loader"></span>} {/* 🔹 loader condicional */}
        </>
      }
      onReiniciar={reiniciarFormulario}
      childrenInicio={
        <div className="formulario">
          <p>Ingrese calle y numero:</p>
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
