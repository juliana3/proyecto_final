import React, { useState, useEffect } from "react"; 
import Ubicacion from "../components/ubicacion"; 
import Formulario from "../components/formulario";
import Modal from "../components/modal"; 
import gif from "../assets/saludo.gif";
import sf from "../assets/SantaFeCapital.png";
import sfuno from "../assets/imagepng.webp";
import sfdos from "../assets/dias.webp";
import senala from "../assets/contento_senalando.svg";
import search from "../assets/Search.gif";

export default function Home() {
  //Funciones abrir modales
  const [mostrarUbicacion, setMostrarUbicacion] = useState(false);
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  //Funciones cerrar modales
  const cerrarModalUbicacion = () => setMostrarUbicacion(false);
  const cerrarModalFormulario = () => setMostrarFormulario(false);
  //Constuctor de imagenes para el carrusel
  const imagenes = [
    sf,
    sfuno,
    sfdos,
  ];
  const [index, setIndex] = useState(0);
  const showSlide = (i) => {
    if (i < 0) setIndex(imagenes.length - 1);
    else if (i >= imagenes.length) setIndex(0);
    else setIndex(i);
  };
  useEffect(() => {
    const timer = setInterval(() => {
      showSlide(index + 1);
    }, 5000);
    return () => clearInterval(timer);
  }, [index]);

  // Renderizado del componente Home
  return (
    <div className="home_conteiner">
      <h1 className="titulos">BasurApp</h1>
      <p> ¡Bienvenido! Acá podés consultar fácilmente 
          cuándo pasa el camión de basura en tu barrio. 
          Mantener la ciudad limpia nunca fue tan fácil. 
          ¡Baja y conoce mas! 
      </p>
      <img src={gif} alt="Saludo" className="saludo" />
      {!mostrarUbicacion && !mostrarFormulario && (
        <button className="btns" onClick={() => setMostrarUbicacion(true)}>
          CONSULTA ACA TU HORARIO DE RECOLECCION
          <img src={search} className="gifs" alt="Buscar" />
        </button>
      )}
      <Modal isOpen={mostrarUbicacion} cerrarModal={cerrarModalUbicacion}>
        <Ubicacion />
        <button className="btns"
          onClick={() => {
            setMostrarUbicacion(false);
            setMostrarFormulario(true);
          }}
        >UTILIZAR OTRA DIRECCION</button>
      </Modal>
      <Modal isOpen={mostrarFormulario} cerrarModal={cerrarModalFormulario}>
        <Formulario />
      </Modal>
      <div className="carousel">
        <div className="carousel-track" style={{ transform: `translateX(${-index * 100}%)` }}>
          {imagenes.map((src, i) => (
            <div className="carousel-slide" key={i}>
              <img src={src} alt={`slide-${i}`} />
            </div>
          ))}
        </div>
        <button className="carousel-btn prev" onClick={() => showSlide(index - 1)}>&#10094;</button>
        <button className="carousel-btn next" onClick={() => showSlide(index + 1)}>&#10095;</button>
      </div>
      <h1 className="titulos">¿Qué es Basurapp?</h1>
      <p> En Santa Fe, los horarios de recolección de basura 
          a veces son difíciles de seguir. <strong>BasurApp </strong>
          es una aplicacion que te permite consultar en tiempo real 
          cuando pasara el camion por tu dirección asegurandote asi
          de que tus residuos se recojan a tiempo, sin sorpresas ni retrasos. <br />
          ¡Descargá la app y empezá a usarla!
        </p>
      <img src={senala} alt="Señalando" width="150px" />
    </div>
  );
}
