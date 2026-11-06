const API = (window.CONFIG.API_BASE || "").replace(/\/+$/, "");

let graficaRegion = null;
let graficaMes = null;


async function obtenerJSON(ruta, parametros = null) {

    let url = API + ruta;

    if (parametros && parametros.toString()) {
        url += "?" + parametros.toString();
    }

    const respuesta = await fetch(url);

    if (!respuesta.ok) {
        throw new Error(
            "Error al consultar la API: " + respuesta.status
        );
    }

    return await respuesta.json();
}


function leerFiltros() {

    const parametros = new URLSearchParams();

    const campos = [
        "region",
        "desde",
        "hasta",
        "min_mag"
    ];

    for (const campo of campos) {

        const valor = document.getElementById(campo).value;

        if (valor !== "") {
            parametros.set(campo, valor);
        }
    }

    return parametros;
}


async function cargarRegiones() {

    const datos = await obtenerJSON("/api/regiones");

    const selector = document.getElementById("region");

    for (const item of datos) {

        const opcion = document.createElement("option");

        opcion.value = item.region;
        opcion.textContent = item.region;

        selector.appendChild(opcion);
    }
}


function crearGraficaRegion(datos) {

    if (graficaRegion) {
        graficaRegion.destroy();
    }

    const principales = datos.slice(0, 10);

    graficaRegion = new Chart(
        document.getElementById("graficaRegion"),
        {
            type: "bar",

            data: {
                labels: principales.map(x => x.region),

                datasets: [{
                    label: "Cantidad de sismos",
                    data: principales.map(x => x.total),
                    backgroundColor: "#2563eb"
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: "y",

                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        }
    );
}


function crearGraficaMes(datos) {

    if (graficaMes) {
        graficaMes.destroy();
    }

    const meses = datos.slice(-12);

    graficaMes = new Chart(
        document.getElementById("graficaMes"),
        {
            type: "line",

            data: {
                labels: meses.map(x => x.periodo),

                datasets: [{
                    label: "Sismos por mes",
                    data: meses.map(x => x.total),
                    borderColor: "#dc2626",
                    backgroundColor: "#fecaca",
                    tension: 0.25,
                    fill: true
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        }
    );
}


function llenarTabla(eventos) {

    const cuerpo = document.getElementById("tablaEventos");

    cuerpo.replaceChildren();

    for (const evento of eventos) {

        const fila = document.createElement("tr");

        const profundidad = evento.profundidad_km == null
            ? "Sin dato"
            : Number(evento.profundidad_km).toFixed(2);

        const valores = [
            String(evento.fecha_utc).slice(0, 19)
                .replace("T", " "),

            Number(evento.magnitud).toFixed(2),

            profundidad,

            evento.region,

            evento.lugar
        ];

        for (const valor of valores) {

            const celda = document.createElement("td");

            celda.textContent = valor;

            fila.appendChild(celda);
        }

        cuerpo.appendChild(fila);
    }
}


async function actualizarDashboard() {

    const mensaje = document.getElementById("mensaje");

    mensaje.textContent = "Consultando eventos sismicos...";

    try {

        const filtros = leerFiltros();

        const [kpis, regiones, meses, eventos] =
            await Promise.all([

                obtenerJSON("/api/kpis", filtros),

                obtenerJSON("/api/por-region", filtros),

                obtenerJSON("/api/por-mes", filtros),

                obtenerJSON("/api/eventos", filtros)

            ]);


        document.getElementById("total").textContent =
            kpis.total;


        document.getElementById("promedio").textContent =
            Number(kpis.magnitud_promedio || 0).toFixed(2);


        document.getElementById("maxima").textContent =
            Number(kpis.magnitud_maxima || 0).toFixed(2);


        crearGraficaRegion(regiones);

        crearGraficaMes(meses);

        llenarTabla(eventos);
        if (typeof window.actualizarMapa === "function") {
    window.actualizarMapa(eventos);
}


        mensaje.textContent =
            "Consulta completada. " +
            eventos.length +
            " eventos mostrados.";

    } catch (error) {

        console.error(error);

        mensaje.textContent =
            "No se pudieron cargar los datos: " +
            error.message;
    }
}


document.getElementById("filtros")
    .addEventListener("submit", function(evento) {

        evento.preventDefault();

        actualizarDashboard();
    });


document.getElementById("limpiar")
    .addEventListener("click", function() {

        document.getElementById("filtros").reset();

        actualizarDashboard();
    });


async function iniciar() {

    try {

        await cargarRegiones();

        await actualizarDashboard();

    } catch (error) {

        console.error(error);

        document.getElementById("mensaje").textContent =
            "Error al iniciar la plataforma: " +
            error.message;
    }
}


iniciar();