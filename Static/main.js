document.addEventListener('DOMContentLoaded', function() {
    console.log("Script cargado.");

    const botonGeolocalizacion = document.getElementById('botonGeolocalizacion');
    const botonManual = document.getElementById('botonManual');
    const direccionForm = document.getElementById('form-direccion');
    const inputDireccion = document.getElementById('direccion');
    const mensaje = document.getElementById('mensaje');
    const resultado = document.getElementById('resultado');

    // Ocultamos todo al inicio
    mensaje.style.display = 'none';
    resultado.style.display = 'none';
    direccionForm.style.display = 'none';


    // --- Opción 1: geolocalización ---
    if (botonGeolocalizacion) {
        botonGeolocalizacion.addEventListener('click', function() {
            resultado.style.display = 'none';
            mostrarMensaje("Obteniendo tu ubicación...", 'blue');
            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        const latitud = pos.coords.latitude;
                        const longitud = pos.coords.longitude;
                        console.log("Ubicación obtenida por GPS:", latitud, longitud);

                        consultarUbicacion({latitud,longitud});
                    },
                    function(err) {
                        console.error("Error geolocalización:", err.message);
                        // Si falla, mostramos el form manual
                        mostrarMensaje("No pudimos obtener tu ubicación. Por favor ingresa la dirección manualmente!", 'red')
                        direccionForm.style.display = 'block'; //muestra el form
                    },
                    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
                );
            } else {
                console.log("Geolocalización no disponible.");
                mostrarMensaje("Tu navegador no soporta geolocalización. Ingresa tu dirección manualmente.", 'red');
                direccionForm.style.display = 'block';
            }
            direccionForm.style.display = 'none'; // Ocultamos el formulario
        });
    }

    // --- Opción 2: ingreso manual ---
    if (botonManual) {
        botonManual.addEventListener('click', function() {
            direccionForm.style.display = 'block'; //muestra el form
            mensaje.style.display = 'none';
            resultado.style.display = 'none';
        });
    }

    // --- Submit manual ---
    if (direccionForm) {
        direccionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const direccion = inputDireccion.value.trim();
            if (direccion) {
                consultarUbicacion({ direccion: direccion });
            } else {
                mostrarMensaje("Por favor, ingresa una dirección valida!", 'red')
            }
        });
    }

    // --- Consulta al backend ---
    function consultarUbicacion(datos) {
        mostrarMensaje("Consultando servicio... por favor esperá.", 'blue');
        fetch('/consultar_ubicacion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        })
        .then(r => r.json())
        .then(data => {
            console.log("Respuesta del backend:", data)
            mostrarResultadoSegunEstado(data)})

        .catch(err => {
            console.error("Error conexión:", err);
            mostrarMensaje("No pudimos conectar con el servidor. Intenta más tarde.", 'red');
        });
    }

    // --- Mostrar mensajes y resultados ---
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
