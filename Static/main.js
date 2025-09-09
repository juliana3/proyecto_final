// Espera a que el DOM esté completamente cargado antes de ejecutar el script.
document.addEventListener('DOMContentLoaded', function() {
    console.log("Script principal cargado.");

    // Obtenemos las referencias a los elementos del DOM una sola vez.
    const addressForm = document.getElementById('address-form');
    const addressInput = document.getElementById('address-input');
    const messageBox = document.getElementById('message-box');
    const resultBox = document.getElementById('result-box');

    // 1. Manejamos el flujo de geolocalización al cargar la página.
    iniciarGeolocalizacion();

    // 2. Manejamos el evento 'submit' del formulario.
    if (addressForm) {
        addressForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Evita el envío del formulario.

            const direccion = addressInput.value;
            if (direccion) {
                // Si el usuario ingresa una dirección, la consultamos directamente.
                consultarDireccionEnBackend(direccion);
            } else {
                // COMENTARIO: En lugar de un 'alert', mostramos el mensaje en la interfaz.
                mostrarMensaje("Por favor, ingresa una dirección válida.", 'bg-red-500');
            }
        });
    }

    /**
     * Intenta obtener la ubicación del navegador para una primera validación.
     */
    function iniciarGeolocalizacion() {
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(
                function(posicion) {
                    const latitud = posicion.coords.latitude;
                    const longitud = posicion.coords.longitude;
                    console.log("Ubicación obtenida por GPS:", latitud, longitud);
                    verificarUbicacionEnBackend(latitud, longitud);
                },
                function(error) {
                    console.error("Error de geolocalización:", error.message);
                    // COMENTARIO: Mensaje amigable para el usuario sin bloquear la interfaz.
                    mostrarMensaje("No pudimos obtener tu ubicación, puedes ingresar tu dirección manualmente.", 'bg-yellow-500');
                    addressForm.style.display = 'block'; // Aseguramos que el formulario esté visible.
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
        } else {
            console.log("Geolocalización no disponible.");
            mostrarMensaje("Tu navegador no soporta geolocalización. Ingresa tu dirección manualmente.", 'bg-red-500');
            addressForm.style.display = 'block';
        }
    }

    /**
     * Envía las coordenadas al backend para verificar si están en Santa Fe.
     */
    function verificarUbicacionEnBackend(lat, lon) {
        fetch('/verificar_ubicacion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitud: lat, longitud: lon })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Respuesta del backend (ubicación):", data);
            if (data.en_santa_fe) {
                mostrarMensaje("Ubicación en Santa Fe verificada. Ahora ingresa tu dirección.", 'bg-green-500');
                addressForm.style.display = 'block';
            } else {
                mostrarMensaje("Tu ubicación no se encuentra en Santa Fe. El servicio solo funciona aquí.", 'bg-red-500');
                addressForm.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error al verificar ubicación:', error);
            mostrarMensaje("Ocurrió un error al verificar tu ubicación. Intenta de nuevo más tarde.", 'bg-red-500');
        });
    }

    /**
     * Envía la dirección de texto al backend para consultar el camión.
     */
    function consultarDireccionEnBackend(direccion) {
        // COMENTARIO: Limpiamos los resultados y mensajes anteriores antes de la consulta.
        mostrarMensaje("Consultando el servicio... por favor espera.", 'bg-blue-500');
        resultBox.textContent = '';

        fetch('/consultar_direccion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ direccion: direccion })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Respuesta del backend (dirección):", data);
            
            // COMENTARIO: Mapeamos los estados del backend a un mensaje y color.
            if (data.tiempo_estimado_llegada) {
                mostrarResultado(data.tiempo_estimado_llegada, 'bg-green-500');
            } else if (data.mensaje) {
                // COMENTARIO: Ahora usamos las funciones auxiliares para todos los casos.
                let estadoColor = 'bg-yellow-500'; // Color por defecto para 'ya_paso'
                if (data.estado && ['fuera_de_servicio', 'finalizado', 'error_configuracion'].includes(data.estado)) {
                    estadoColor = 'bg-red-500';
                }
                mostrarResultado(data.mensaje, estadoColor);
            } else {
                mostrarMensaje("No se pudo obtener el estado del camión. Intenta de nuevo.", 'bg-yellow-500');
            }
        })
        .catch(error => {
            console.error('Error al consultar la dirección:', error);
            mostrarMensaje("Ocurrió un error al procesar tu solicitud.", 'bg-red-500');
        });
    }

    /**
     * Muestra un mensaje en el cuadro de mensajes.
     */
    function mostrarMensaje(mensaje, cssClass) {
        messageBox.textContent = mensaje;
        messageBox.className = `mt-6 p-4 rounded-lg text-center font-semibold text-white transition-opacity duration-500 ${cssClass}`;
        resultBox.textContent = ''; // Aseguramos que el otro cuadro esté vacío.
    }

    /**
     * Muestra el resultado de la consulta.
     */
    function mostrarResultado(mensaje, cssClass) {
        resultBox.textContent = mensaje;
        resultBox.className = `mt-6 p-4 rounded-lg text-center font-semibold text-white transition-opacity duration-500 ${cssClass}`;
        messageBox.textContent = '';
    }
});