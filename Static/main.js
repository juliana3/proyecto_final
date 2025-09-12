// Espera a que el DOM esté completamente cargado antes de ejecutar el script.
document.addEventListener('DOMContentLoaded', function() {
    console.log("Script principal cargado.");

    // Obtenemos las referencias a los elementos del DOM.
    const botonGeolocalizacion = document.getElementById('botonGeolocalizacion');
    const botonManual = document.getElementById('botonManual');
    const direccionForm = document.getElementById('form-direccion');
    const imputDireccion = document.getElementById('direccion');
    const mensaje = document.getElementById('mensaje');
    const resultado = document.getElementById('resultado');

    // Inicialmente, ocultamos los cuadros de resultados
    mensaje.style.display = 'none';
    resultado.style.display = 'none';
    direccionForm.style.display = 'none';

    // Manejamos el clic en el botón de geolocalización. Si se presiona, se inicia la geolocalización y se oculta el formulario.
    if (botonGeolocalizacion) {
        botonGeolocalizacion.addEventListener('click', function() {
            mensaje.style.display = 'block';
            resultado.style.display = 'none';
            iniciarGeolocalizacion();
            direccionForm.style.display = 'none'; // Ocultamos el formulario
        });
    }

    // Manejamos el clic en el botón de entrada manual. Si se presiona, se muestra el formulario y se ocultan los mensajes anteriores.
    if (botonManual) {
        botonManual.addEventListener('click', function() {
            direccionForm.style.display = 'block'; // Mostramos el formulario
            mensaje.style.display = 'none';
            resultado.style.display = 'none';
        });
    }

    // Manejamos el evento 'submit' del formulario. Cuando se envía, se previene el comportamiento por defecto y se obtiene la dirección ingresada.
    if (direccionForm) {
        direccionForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const direccion = imputDireccion.value;
            if (direccion) {
                // Se llama a la función unificada con la dirección
                consultarUbicacion({ direccion: direccion });
            } else {
                mostrarMensaje("Por favor, ingresa una dirección válida.", 'red');
            }
        });
    }


   

    // Funciones principales

    // Función para iniciar la geolocalización del usuario
    function iniciarGeolocalizacion() {
        mostrarMensaje("Obteniendo tu ubicación...", 'blue');
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(
                function(posicion) {
                    const latitud = posicion.coords.latitude;
                    const longitud = posicion.coords.longitude;
                    console.log("Ubicación obtenida por GPS:", latitud, longitud);
                    // Se llama a la función unificada con las coordenadas
                    consultarUbicacion({ latitud: latitud, longitud: longitud });
                },
                function(error) {
                    console.error("Error de geolocalización:", error.message);
                    mostrarMensaje("No pudimos obtener tu ubicación. Por favor, ingresa tu dirección manualmente.", 'orange');
                    direccionForm.style.display = 'block';
                    // Deshabilitamos el botón para evitar que el usuario vuelva a intentarlo sin éxito.
                    deshabilitarBotonGeolocalizacion();
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
        } else {
            console.log("Geolocalización no disponible.");
            mostrarMensaje("Tu navegador no soporta geolocalización. Ingresa tu dirección manualmente.", 'red');
            direccionForm.style.display = 'block';
            // Deshabilitamos el botón si la función no es compatible
            deshabilitarBotonGeolocalizacion();
        }
    }

    // Función unificada que envía los datos al backend
    function consultarUbicacion(datos) {
        mostrarMensaje("Consultando el servicio... por favor espera.", 'blue');
        fetch('/consultar_ubicacion', { //es la ruta que esta en app.py
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        })
        .then(response => response.json())
        .then(data => {
            console.log("Respuesta del backend:", data);
            mostrarResultadoSegunEstado(data);
        })
        .catch(error => {
            console.error('Error al consultar ubicación:', error);
            mostrarMensaje("Ocurrió un error al procesar tu solicitud. Intenta de nuevo más tarde.", 'red');
        });
    }

    // Función para deshabilitar el botón de geolocalización y cambiar su estilo. Sirve para cuando la geolocalización falla o no es compatible y el usaurio debe ingresar la dirección manualmente. Lo bloquea para que no se siga intentando con la geolocalización.
    function deshabilitarBotonGeolocalizacion() {
        if (botonGeolocalizacion) {
            botonGeolocalizacion.disabled = true;
            botonGeolocalizacion.style.backgroundColor = '#d1d5db'; // un color gris claro
            botonGeolocalizacion.style.cursor = 'not-allowed';
            botonGeolocalizacion.textContent = 'Ubicación deshabilitada';
        }
    }

    

    // Funciones auxiliares para mostrar mensajes y resultados.
    function mostrarMensaje(mensaje_segun_estado, color) {
        //lo de los colores se elimina cuando este hecho el css. Los colores no representan nada, son para diferenciar los estados. Eran para probar
        let backgroundColor = 'yellow'; // Por defecto
        switch(color) {
            case 'blue': backgroundColor = '#3B82F6'; break;
            case 'red': backgroundColor = '#EF4444'; break;
            case 'orange': backgroundColor = '#F59E0B'; break;
        }

        mensaje.textContent = mensaje_segun_estado;
        mensaje.style.display = 'block';
        mensaje.style.backgroundColor = backgroundColor;
        mensaje.style.color = 'white';
        mensaje.style.fontWeight = 'bold';
        mensaje.style.padding = '1rem';
        mensaje.style.borderRadius = '0.5rem';
        mensaje.style.textAlign = 'center';
        mensaje.style.position = 'fixed';
        mensaje.style.top = '50%';
        mensaje.style.left = '50%';
        mensaje.style.transform = 'translate(-50%, -50%)';
        mensaje.style.zIndex = '1000'; // Asegura que esté por encima de otros elementos

        resultado.style.display = 'none';
    }

    function mostrarResultado(mensaje_segun_estado, color) {
        let backgroundColor = 'green'; // Por defecto
        switch(color) {
            case 'green': backgroundColor = '#22C55E'; break;
            case 'red': backgroundColor = '#EF4444'; break;
            case 'yellow': backgroundColor = '#F59E0B'; break;
        }

        resultado.textContent = mensaje_segun_estado;
        resultado.style.display = 'block';
        resultado.style.backgroundColor = backgroundColor;
        resultado.style.color = 'white';
        resultado.style.fontWeight = 'bold';
        resultado.style.padding = '1rem';
        resultado.style.borderRadius = '0.5rem';
        resultado.style.textAlign = 'center';
        
        // Agregando las siguientes líneas para centrar
        resultado.style.position = 'fixed';
        resultado.style.top = '50%';
        resultado.style.left = '50%';
        resultado.style.transform = 'translate(-50%, -50%)';
        resultado.style.zIndex = '1000'; // Asegura que esté por encima de otros elementos
        
        mensaje.style.display = 'none';
    }

    function mostrarResultadoSegunEstado(data) {
        if (data.tiempo_estimado_llegada) {
            mostrarResultado(data.tiempo_estimado_llegada, 'green');
        } else if (data.mensaje) {
            let estadoColor = 'yellow';
            if (data.estado && ['fuera_de_servicio', 'finalizado', 'error_configuracion', 'no_iniciado', 'ya_paso_por_su_direccion'].includes(data.estado)) {
                estadoColor = 'red';
            }
            mostrarResultado(data.mensaje, estadoColor);
        } else {
            mostrarMensaje("No se pudo obtener el estado del camión. Intenta de nuevo.", 'red');
        }
    }
});
