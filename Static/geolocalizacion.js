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
    // Usar Fetch API para enviar los datos por POST al servidor
    fetch('/verificar_ubicacion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ latitud: latitud, longitud: longitud })
    })
    .then(response => {
        // Si la respuesta no es exitosa, lanzar un error
        if (!response.ok) {
            throw new Error('La respuesta del servidor no fue exitosa. Estado: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        //  Manejar la respuesta del backend
        console.log("Respuesta del backend:", data);

        // Validar si el usuario está en la ciudad de Santa Fe
        if (!data.en_santa_fe) {
            alert("Parece que no estás en la ciudad de Santa Fe. Nuestra aplicación solo funciona en esta zona.");
            // Aquí puedes deshabilitar el formulario o redirigir al usuario
        } 
        // Si está en la ciudad pero no en el área de servicio
        else if (!data.en_area_servicio) {
            alert("Estás en Santa Fe, pero fuera de nuestra área de servicio. Por favor, ingresa una dirección completa dentro del área para usar la aplicación.");
            // Aquí puedes mostrar un mensaje, pero se le permite al usuario ingresar una dirección
        } 
        // Si está en el área de servicio
        else {
            console.log("El usuario está en el área de servicio de Santa Fe. ¡Todo listo para continuar!");
            // Aquí puedes habilitar el formulario o cualquier otro elemento de la UI
            // Por ejemplo:
            // document.getElementById('formulario-direccion').style.display = 'block';
            alert("¡Bienvenido! Estás en nuestra área de servicio.");
        }
    })
    .catch(error => {
        console.error('Error al enviar ubicación al backend:', error);
        alert("Ocurrió un error al verificar tu ubicación. Por favor, intenta de nuevo más tarde.");
    });
}
