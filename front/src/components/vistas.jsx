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
          <DotLottieReact className="lottie"
            src="https://lottie.host/9002ff25-648d-4a22-b64b-c7e99d1af878/m0pylI6wwh.lottie"
            loop
            autoplay
          />
        </div>
      )}
      {estado === "resultado" && (
        <div style={{ textAlign: "center" }}>
          <p>{resultado}</p>
          <div className="advertencia">
            <img src={advertencia} alt="" className="adv" />
            <p className="textAdv">
              Si hay alerta meteorológico o llueve no la saques
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
