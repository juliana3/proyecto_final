import { useState, useRef } from "react";
import axios from "axios";
import Vistas from "../components/vistas";

export default function Formulario() {
  const [direccion, setDireccion] = useState("");
  const [resultado, setResultado] = useState(null);
  const [mensaje, setMensaje] = useState(null);
  const [estado, setEstado] = useState("inicio");
  const timeoutRef = useRef(null);

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

    setTimeout(() => {
      setEstado("resultado");
      timeoutRef.current = setTimeout(() => {
        reiniciarFormulario();
      }, 10000);
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
      setResultado("Por favor, ingresa una dirección válida!");
      setEstado("resultado");
      timeoutRef.current = setTimeout(() => reiniciarFormulario(), 5000);
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
  };

  return (
    <Vistas
      estado={estado}
      mensaje={mensaje}
      resultado={resultado}
      onReiniciar={reiniciarFormulario}
      childrenInicio={
        <>
          <h3 style={{ marginTop: 0 }}>Consultar Ubicación</h3>
          <div>
            <input
              type="text"
              placeholder="Escribí tu dirección"
              value={direccion}
              onChange={(e) => setDireccion(e.target.value)}
              style={{
                padding: "8px",
                width: "calc(100% - 100px)",
                marginRight: "8px",
                borderRadius: "6px",
                border: "1px solid #ccc",
              }}
            />
            <button
              onClick={enviarDireccion}
              style={{
                padding: "8px 12px",
                backgroundColor: "#3bcf60",
                color: "#0c3324",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
              }}
            >
              Enviar dirección
            </button>
          </div>
        </>
      }
    />
  );
}
