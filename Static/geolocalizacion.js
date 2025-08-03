//geolocalizacion.js


// Este script se encarga de obtener la ubicación del usuario a través del navegador,
// enviarla al backend para su validación y mostrar un mensaje apropiado.

// Se ejecuta una vez que el DOM (la estructura HTML de la página) ha cargado por completo.
document.addEventListener('DOMContentLoaded', function() {
    console.log("Script de geolocalización cargado.");
    obtenerUbicacion();
});

/**
 * Función principal para obtener la ubicación del usuario.
 * Utiliza la API de geolocalización del navegador.
 */
function obtenerUbicacion() {
    //Verificar si el navegador soporta la API de geolocalización
    if ("geolocation" in navigator) {
        // Pedir la ubicación actual del usuario con un timeout de 10 segundos
        navigator.geolocation.getCurrentPosition(
            // Función si la ubicación se obtiene con éxito
            function(posicion) {
                const latitud = posicion.coords.latitude;
                const longitud = posicion.coords.longitude;
                
                console.log("Ubicación obtenida:", latitud, longitud);
                
                // Enviar las coordenadas al backend para su validación
                verificarUbicacionEnBackend(latitud, longitud);
            },
            // Función si hay un error
            function(error) {
                console.error("Error al obtener la ubicación:", error.message);
                if (error.code === error.PERMISSION_DENIED) {
                    alert("Por favor, permite el acceso a tu ubicación para usar la aplicación. Si deniegas el permiso, la aplicación solo funcionará si ya estás en el área de servicio.");
                } else {
                    alert("Ocurrió un error al obtener tu ubicación. Si el problema persiste, revisa la configuración de tu navegador.");
                }
            },
            // Opciones de configuración para la geolocalización
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    } else {
        // Si el navegador no tiene soporte para geolocalización
        console.log("Geolocalización no está disponible en este navegador.");
        alert("Tu navegador no soporta geolocalización. La aplicación no podrá verificar tu ubicación.");
    }
}

/**
 * Envía las coordenadas al backend y maneja la respuesta del servidor.
 * @param {number} latitud - La latitud del usuario.
 * @param {number} longitud - La longitud del usuario.
 */

function verificarUbicacionEnBackend(latitud, longitud) {
    fetch('/verificar_ubicacion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ latitud: latitud, longitud: longitud })
    })
    .then(response => response.json())
    .then(data => {
        const messageBox = document.getElementById('message-box');
        const addressForm = document.getElementById('address-form');

        console.log("Respuesta del backend:", data);

        // Si la verificación de Santa Fe es exitosa, muestra el formulario
        if (data.en_santa_fe) {
            messageBox.textContent = "Ubicación en Santa Fe verificada. Ahora ingresa tu dirección.";
            messageBox.className = "mt-6 p-4 rounded-lg text-center font-semibold text-white transition-opacity duration-500 bg-green-500";
            addressForm.style.display = 'block';
        } else {
            messageBox.textContent = "Tu ubicación no se encuentra en la ciudad de Santa Fe. Nuestra aplicación solo funciona en esta zona.";
            messageBox.className = "mt-6 p-4 rounded-lg text-center font-semibold text-white transition-opacity duration-500 bg-red-500";
            addressForm.style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error al enviar ubicación al backend:', error);
        const messageBox = document.getElementById('message-box');
        messageBox.textContent = "Ocurrió un error al verificar tu ubicación.";
        messageBox.className = "mt-6 p-4 rounded-lg text-center font-semibold text-white transition-opacity duration-500 bg-red-500";
    });
}