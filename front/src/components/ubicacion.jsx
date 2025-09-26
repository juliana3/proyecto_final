import { useState, useRef } from "react";
import axios from "axios";
import { DotLottieReact } from "@lottiefiles/dotlottie-react";

export default function Geolocalizacion() {
  const [resultado, setResultado] = useState(null);
  const [mensaje, setMensaje] = useState(null);
  const [estado, setEstado] = useState("inicio");
  const [usandoUbicacion, setUsandoUbicacion] = useState(false);

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

  const enviarCoordenadas = () => {
    setMensaje("Obteniendo tu ubicación...");
    setEstado("cargando");
    setUsandoUbicacion(true);

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        consultarUbicacion({
          latitud: pos.coords.latitude,
          longitud: pos.coords.longitude,
        }).finally(() => setUsandoUbicacion(false));
      },
      () => {
        setResultado("No pudimos obtener tu ubicación. Ingresá la dirección manualmente!");
        setEstado("resultado");
        setUsandoUbicacion(false);
        timeoutRef.current = setTimeout(() => reiniciarFormulario(), 5000);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  };

  const reiniciarFormulario = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setResultado(null);
    setMensaje(null);
    setEstado("inicio");
    setUsandoUbicacion(false);
  };

  return (
    <div style={{ padding: "1rem" }}>
      {estado === "inicio" && (
        <button
          onClick={enviarCoordenadas}
          style={{
            padding: "8px 12px",
            backgroundColor: "#3bcf60",
            color: "#0c3324",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          Usar mi ubicación actual
        </button>
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
            Intentar nuevamente
          </button>
        </div>
      )}
    </div>
  );
}
