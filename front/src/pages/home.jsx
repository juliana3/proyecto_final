import React, { useState } from "react"; 
import Ubicacion from "../components/ubicacion"; 
import Formulario from "../components/formulario";
import Modal from "../components/modal"; 
import gif from "../assets/saludo.gif";
import carrusel from "../assets/Separar.jpg";
import senala from "../assets/contento_senalando.svg";
import search from "../assets/Search.gif";

export default function Home() {
  const [mostrarUbicacion, setMostrarUbicacion] = useState(false);
  const [mostrarFormulario, setMostrarFormulario] = useState(false);

  // Funciones para cerrar modales
  const cerrarModalUbicacion = () => setMostrarUbicacion(false);
  const cerrarModalFormulario = () => setMostrarFormulario(false);

  return (
    <div className="home_conteiner">
      <h1 className="titulos">BasurApp</h1>
      <p>
        Bienvenido, aca vas a poder consultar en cuanto pasa el camión recolector.
        <br />
        Ayudemos a mantener más limpia la ciudad.
        <br />
        Scrollea y conoce mas!
      </p>

      <img src={gif} alt="Saludo" className="saludo" />

      {/* Botón solo aparece cuando no hay ningún modal abierto */}
      {!mostrarUbicacion && !mostrarFormulario && (
        <button className="btns" onClick={() => setMostrarUbicacion(true)}>
          CONSULTA ACA TU HORARIO DE RECOLECCION
          <img src={search} className="gifs" alt="Buscar" />
        </button>
      )}

      {/* Modal de Ubicacion */}
      <Modal isOpen={mostrarUbicacion} cerrarModal={cerrarModalUbicacion}>
        <Ubicacion />
        <button
          onClick={() => {
            setMostrarUbicacion(false); // cerrar modal actual
            setMostrarFormulario(true); // abrir formulario
          }}
          style={{
            padding: "8px 12px",
            backgroundColor: "#3bcf60",
            color: "#0c3324",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            marginTop: "1rem",
          }}
        >
          Otra dirección!!!
        </button>
      </Modal>

      {/* Modal de Formulario */}
      <Modal isOpen={mostrarFormulario} cerrarModal={cerrarModalFormulario}>
        <Formulario />
      </Modal>

      <br /><br />
      <img src={carrusel} alt="Carrusel" width="350px" />
      <br />
      <h1 className="titulos">Qué es Basurapp?</h1>
      <br />
      <p>
        La ciudad de Santa Fe enfrenta en la actualidad serias dificultades vinculadas a la recolección de residuos domiciliarios. 
        Aunque desde el municipio se han establecido cronogramas y horarios específicos para cada barrio, en la práctica, la ventana horaria asignada resulta demasiado amplia.
        <br />
        Sabemos que muchas veces no se respetan los horarios o incluso se omite por completo el recorrido en determinadas zonas.
        <br />
        Para resolver esto, te proponemos “BasurApp”, un programa que te va a permitir consultar en tiempo real la ubicación del camión recolector para la dirección que solicites.
      </p>
      <img src={senala} alt="Señalando" width="100px" />
    </div>
  );
}
