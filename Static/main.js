document.addEventListener('DOMContentLoaded', function() {
    const addressForm = document.getElementById('address-form');
    if (addressForm) {
        addressForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const addressInput = document.getElementById('address-input');
            const direccion = addressInput.value;

            if (direccion) {
                consultarDireccionEnBackend(direccion);
            } else {
                alert("Por favor, ingresa una dirección válida.");
            }
        });
    }
});

function consultarDireccionEnBackend(direccion) {
    const resultBox = document.getElementById('result-box');

    fetch('/consultar_direccion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ direccion: direccion })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Respuesta del backend para la dirección:", data);

        // Definimos colores según el estado
        const estados = {
            'en_ruta': 'bg-green-500',
            'ya_paso_por_su_direccion': 'bg-yellow-500',
            'turno_terminado': 'bg-red-500',
            'fuera_de_servicio': 'bg-red-500',
            'sin_servicio_en_esta_zona': 'bg-red-500',
            'no_camion_en_ruta': 'bg-red-500',
            'error_configuracion': 'bg-red-500'
        };

        // Mostramos siempre el mensaje del backend
        if (data.mensaje) {
            resultBox.textContent = data.mensaje;
            const color = estados[data.estado] || 'bg-yellow-500';
            resultBox.className = `mt-6 p-4 rounded-lg text-center font-semibold text-white transition-opacity duration-500 ${color}`;
        } else {
            resultBox.textContent = "No se encontró información del camión para esta dirección. AAAAA";
            resultBox.className = "mt-6 p-4 rounded-lg text-center font-semibold text-white transition-opacity duration-500 bg-yellow-500";
        }
    })
    .catch(error => {
        console.error('Error al consultar la dirección:', error);
        resultBox.textContent = "Ocurrió un error al procesar tu solicitud.";
        resultBox.className = "mt-6 p-4 rounded-lg text-center font-semibold text-white transition-opacity duration-500 bg-red-500";
    });
}
