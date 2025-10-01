import { useState, useRef } from "react";
import axios from "axios";
import Vistas from "../components/vistas";

export default function Ubicacion() {
  const [resultado, setResultado] = useState(null);
  const [mensaje, setMensaje] = useState(null);
  const [estado, setEstado] = useState("inicio");
  const timeoutRef = useRef(null);

  //consume el servicio de backend
  const consultarUbicacion = async (datos) => {
    setResultado(null);
    setMensaje("Consultando servicio... por favor esperá.");
    setEstado("cargando");
    try {
      //endpoint al backend
      const res = await axios.post("http://localhost:4000/consultar_ubicacion", datos);
      mostrarResultadoSegunEstado(res.data);
    } catch (err) {
      setResultado("No pudimos conectar con el servidor. Intenta más tarde.");
    }

    //timer para cerrar por inectividad y cambiar de modal
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

  const enviarCoordenadas = () => {
    setMensaje("Obteniendo tu ubicación...");
    setEstado("cargando");

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        consultarUbicacion({
          latitud: pos.coords.latitude,
          longitud: pos.coords.longitude,
        });
      },
      () => {
        setResultado("No pudimos obtener tu ubicación. Ingresá la dirección manualmente!");
        setEstado("resultado");
        timeoutRef.current = setTimeout(() => reiniciarFormulario(), 5000);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  };

  //funcion para poder volver a hacer otra consulta
  const reiniciarFormulario = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
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
        <button className="btns" onClick={enviarCoordenadas}>USAR MI UBICACION ACTUAL</button>
      }
    />
  );
}
