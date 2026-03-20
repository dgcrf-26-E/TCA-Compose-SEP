// script_map_info.js: muestra una lista de oficinas por estado al hacer clic en el mapa
document.addEventListener("DOMContentLoaded", () => {
  const svg = d3.select("#mapSvg");
  const contenido = svg.select("g"); // grupo a transformar
  const width = +svg.attr("width");
  const height = +svg.attr("height");

  let modalTimeout;

  // Configuración de zoom
  const zoom = d3
    .zoom()
    .scaleExtent([0.5, 10])
    .on("zoom", (event) => {
      contenido.attr("transform", event.transform);
    });

  svg.call(zoom);

  function zoomToElement(el) {
    const bbox = el.getBBox(); // caja del elemento
    const scale = Math.min(width / bbox.width, height / bbox.height) * 0.5; // zoom automático
    const tx = width / 2 - (bbox.x + bbox.width / 2) * scale;
    const ty = height / 2 - (bbox.y + bbox.height / 2) * scale;

    const transform = d3.zoomIdentity.translate(tx, ty).scale(scale);

    svg.transition().duration(750).call(zoom.transform, transform);
  }

  // Evento de clic sobre cualquier figura dentro de map-data para zoom
  contenido.selectAll("path, rect, circle").on("click", function (event) {
    // Si es un estado, el modal se maneja por separado pero el zoom aplica a todos
    zoomToElement(this);
  });

  // Reset
  d3.select("#resetButton").on("click", () => {
    svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
  });

  const container = document.querySelector(".map-container");
  const tooltip = document.getElementById("tooltip");
  const states = document.querySelectorAll("#mapSvg .state");

  const el = document.getElementById("datos_mapa");
  if (!el) return console.error('No se encontró el script con id "datos_mapa".');

  let datos;
  try {
    datos = JSON.parse(el.textContent);
  } catch (err) {
    console.error("Error parseando JSON:", err);
    return;
  }

  function showTooltip(name, clientX, clientY) {
    tooltip.textContent = name;
    tooltip.style.display = "block";
    const rect = container.getBoundingClientRect();
    const left = clientX - rect.left;
    const top = clientY - rect.top;
    const offsetY = 10;
    tooltip.style.left = `${left}px`;
    tooltip.style.top = `${top - offsetY}px`;
    tooltip.setAttribute("aria-hidden", "false");
  }

  function hideTooltip() {
    tooltip.style.display = "none";
    tooltip.setAttribute("aria-hidden", "true");
  }

  function normalizeName(str) {
    return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
  }

  function getOfficesForState(stateTitle) {
    const normTitle = normalizeName(stateTitle);
    for (const key in datos) {
      if (normalizeName(key).includes(normTitle) || normTitle.includes(normalizeName(key))) {
        return datos[key];
      }
    }
    return null;
  }

  // Pintar mapa: estados con oficinas en azul claro, sin oficinas en gris
  states.forEach((estado) => {
    const nombre = estado.getAttribute("title");
    const oficinasDelEstado = getOfficesForState(nombre);
    
    if (oficinasDelEstado && oficinasDelEstado.length > 0) {
      estado.style.fill = "#60a5fa"; // Azul claro de Tailwind
    } else {
      estado.style.fill = "#cbd5e1"; // Gris suave
    }

    // Handlers de Tooltip
    estado.addEventListener("mouseenter", (e) => {
      showTooltip(nombre, e.clientX, e.clientY);
    });
    estado.addEventListener("mousemove", (e) => {
      showTooltip(nombre, e.clientX, e.clientY);
    });
    estado.addEventListener("mouseleave", hideTooltip);

    // Handlers de Modal (Click)
    estado.addEventListener("click", () => {
      clearTimeout(modalTimeout);
      modalTimeout = setTimeout(() => {
        const modal = document.getElementById("modal");
        const modalTitle = document.getElementById("modalTitle");
        const tbody = document.getElementById("mi-tbody");

        modalTitle.textContent = nombre;
        tbody.innerHTML = "";

        const oficinas = getOfficesForState(nombre);
        if (oficinas && oficinas.length > 0) {
          oficinas.forEach((oficina, index) => {
            const tr = document.createElement("tr");
            
            const tdIndex = document.createElement("td");
            tdIndex.className = "border border-gray-300 px-4 py-2 text-center";
            tdIndex.textContent = index + 1;
            
            const tdNombre = document.createElement("td");
            tdNombre.className = "border border-gray-300 px-4 py-2";
            tdNombre.textContent = oficina;

            tr.appendChild(tdIndex);
            tr.appendChild(tdNombre);
            tbody.appendChild(tr);
          });
        } else {
          const tr = document.createElement("tr");
          const td = document.createElement("td");
          td.setAttribute("colspan", "2");
          td.className = "border border-gray-300 px-4 py-2 text-center text-gray-500 italic";
          td.textContent = "No hay oficinas registradas en este estado.";
          tr.appendChild(td);
          tbody.appendChild(tr);
        }

        modal.style.display = "block";
      }, 300); // Un delay menor para mayor respuesta
    });
  });

  // Cerrar modal localmente
  const closeModal = document.getElementById("closeModal");
  if (closeModal) {
    closeModal.addEventListener("click", () => {
      document.getElementById("modal").style.display = "none";
      // Opcional: reiniciar zoom al cerrar
      svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
    });
  }

  window.addEventListener("click", (e) => {
    const modal = document.getElementById("modal");
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });
});
