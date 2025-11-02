import { useState } from "react";
import Vistas from "../components/vistas";

const escenariosDemo = [
  { nombre: "Ubicación actual fuera de Santa Fe", mensaje: "🚫 Tu dispositivo no se encuentra en la ciudad de Santa Fe. Por favor ingresá la dirección manualmente." },

  { nombre: "Ubicación actual en Santa Fe pero fuera de área de servicio", mensaje: "Estás en Santa Fe, pero fuera del área de servicio de recolección." },

  { nombre: "Ubicación dentro de zona de servicio - CERCA", mensaje: "⏳ El camión más cercano pasa en 20 minutos. ¡Prepará tus residuos!" },

  { nombre: "Ubicación dentro de zona de servicio - LEJOS", mensaje: "🕒 El camión más cercano llegará en 1 hora(s) y 30 minuto(s) ¡Tené todo listo!" },

  { nombre: "Camión a punto de llegar", mensaje: "🚛 ¡El camión está a punto de llegar a tu dirección, en menos de 1 minuto!" },

  { nombre: "Camión ya pasó", mensaje: "👍 Hoy el camión ya pasó. Mañana regresamos entre las 8:00Hs y las 12:00Hs." },

  { nombre: "No hay camiones disponibles", mensaje: "ℹ️ No hay camiones disponibles en tu zona por ahora. Probá en unos minutos!" },

  { nombre: "Error interno", mensaje: "⚠️ Hubo un error interno. No encontramos la ruta del camión. Probá en unos minutos!" },

  { nombre: "Aún no comenzó el turno", mensaje: "⌛ ¡Todavía no comenzamos! Pasaremos a tu dirección entre las 19:00 y las 00:00." },

  { nombre: "Consulta fuera del horario de recolección general", mensaje:	"🚫 ¡Ups! No estamos en servicio ahora. Nuestro horario es de 8:00 a 00:00." },

  { nombre: "Dirección inválida", mensaje: "📍 Dirección no válida. Vas a ser redirigido otra vez." },

  { nombre: "Dirección en zona no cubierta", mensaje: "Estás en Santa Fe, pero fuera del área de servicio de recolección." }

];

export default function Demo() {
  const [estado, setEstado] = useState("inicio");
  const [resultado, setResultado] = useState(null);

  const mostrarEscenario = (mensaje) => {
    setResultado(mensaje);
    setEstado("resultado");
  };

  const reiniciar = () => {
    setResultado(null);
    setEstado("inicio");
  };

  return (
    <Vistas
      estado={estado}
      resultado={resultado}
      onReiniciar={reiniciar}
      childrenInicio={
        <div>
          <h2>Modo Demo</h2>
          <p>Seleccioná un escenario para simular la respuesta del sistema:</p>
          {escenariosDemo.map((esc, i) => (
            <button key={i} className="btns" onClick={() => mostrarEscenario(esc.mensaje)}>
              {esc.nombre}
            </button>
          ))}
        </div>
      }
    />
  );
}
