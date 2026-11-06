let mapa = null;
let marcadores = null;

document.addEventListener("DOMContentLoaded", function () {

    mapa = L.map("mapa-epicentros").setView([20, -20], 2);

    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap'
    }).addTo(mapa);

    marcadores = L.layerGroup().addTo(mapa);

});


window.actualizarMapa = function (eventos) {

    if (!mapa || !marcadores) {
        return;
    }

    marcadores.clearLayers();

    let coordenadas = [];

    for (const evento of eventos) {

        if (evento.latitud == null || evento.longitud == null) {
            continue;
        }

        const latitud = Number(evento.latitud);
        const longitud = Number(evento.longitud);

        if (!Number.isFinite(latitud) || !Number.isFinite(longitud)) {
            continue;
        }

        const magnitud = Number(evento.magnitud);

        let color = "green";

        if (magnitud >= 5) {
            color = "orange";
        }

        if (magnitud >= 6) {
            color = "red";
        }

        const marcador = L.circleMarker(
            [latitud, longitud],
            {
                radius: 8,
                color: color,
                fillColor: color,
                fillOpacity: 0.7
            }
        );

        const informacion = document.createElement("div");

        const titulo = document.createElement("strong");
        titulo.textContent = evento.lugar || "Ubicación desconocida";

        const detalles = document.createElement("p");

        detalles.textContent =
            "Magnitud: " + magnitud.toFixed(2) +
            "\nProfundidad: " + (evento.profundidad_km ?? "Sin dato") + " km" +
            "\nRegión: " + (evento.region || "Sin región") +
            "\nFecha: " + (evento.fecha_utc || "Sin fecha") +
            "\nLatitud: " + latitud +
            "\nLongitud: " + longitud;

        detalles.style.whiteSpace = "pre-line";

        informacion.appendChild(titulo);
        informacion.appendChild(detalles);

        marcador.bindPopup(informacion);

        marcador.addTo(marcadores);

        coordenadas.push([latitud, longitud]);
    }

    if (coordenadas.length > 0) {

        mapa.fitBounds(coordenadas, {
            padding: [20, 20],
            maxZoom: 5
        });

    } else {

        mapa.setView([20, -20], 2);
    }

    setTimeout(function () {
        mapa.invalidateSize();
    }, 200);

};