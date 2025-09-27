// src/components/Vistas.jsx
import { DotLottieReact } from "@lottiefiles/dotlottie-react";
import advertencia from "../assets/advertencia.png";

export default function Vistas({ estado, mensaje, resultado, onReiniciar, childrenInicio }) {
  return (
    <div style={{ padding: "1rem" }}>
      {estado === "inicio" && (
        <>
          {childrenInicio}
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
            onClick={onReiniciar}
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
          <div>
            <img src={advertencia} alt="" width="100px" />
            <h3>
              Si está lloviendo o hay alerta meteorológico no saques la bolsa
              <br />
              Evitemos que se tapen los desagües y mantengamos una ciudad limpia
            </h3>
          </div>
        </div>
      )}
    </div>
  );
}
