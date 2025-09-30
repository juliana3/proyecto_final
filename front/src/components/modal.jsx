export default function Modal({ isOpen, children, cerrarModal }) {
  if (!isOpen) return null;

  return (
    <div className="modal">
      <div className="modal-content">
        {children}
        <button onClick={cerrarModal} className="x">X</button>
      </div>
    </div>
  );
}

