import { useState, useRef } from "react";
import axios from "axios";
import { DotLottieReact } from "@lottiefiles/dotlottie-react";

export default function Formulario() {
  const [direccion, setDireccion] = useState("");
  const [resultado, setResultado] = useState(null);
  const [mensaje, setMensaje] = useState(null);
  const [estado, setEstado] = useState("inicio");

  // ref para guardar timeout del cierre automático
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

    // después de 5s mostrar resultado
    setTimeout(() => {
      setEstado("resultado");
      // programamos cierre automático en 10s
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
    <div style={{ padding: "1rem" }}>
      {estado === "inicio" && (
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
      )}

      {estado === "cargando" && (
        <div style={{ textAlign: "center" }}>
          <h3>{mensaje}</h3>
          <DotLottieReact
            src="https://lottie.host/9002ff25-648d-4a22-b64b-c7e99d1af878/m0pylI6wwh.lottie"
            loop
            autoplay
            style={{ width: 150, height: 150, margin: "0 auto" }}
          />
        </div>
      )}

      {estado === "resultado" && (
        <div style={{ textAlign: "center" }}>
          <h3>Resultado:</h3>
          <p>{resultado}</p>
          <button
            onClick={reiniciarFormulario}
            style={{
              padding: "8px 12px",
              backgroundColor: "#3bcf60",
              color: "#0c3324",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
            }}
          >
            Hacer otra consulta!!!
          </button>
        </div>
      )}
    </div>
  );
}
