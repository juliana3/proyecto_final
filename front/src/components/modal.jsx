export default function Modal({ isOpen, children, cerrarModal }) {
  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0, left: 0, right: 0, bottom: 0,
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          background: 'black',
          padding: '2rem',
          borderRadius: '8px',
          minWidth: '300px',
          textAlign: 'center',
        }}
      >
        {children}

        {/* Botón de cerrar que siempre estará en el modal */}
        <br></br>
        <button
          onClick={cerrarModal} // simplemente cierra todo el modal
          style={{
            marginTop: '1rem',
            padding: '8px 12px',
            backgroundColor: '#3bcf60',
            color: '#0c3324',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
          }}
        >
          Cerrar / Finalizar
        </button>
      </div>
    </div>
  );
}

