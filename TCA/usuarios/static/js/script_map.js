// script.js: muestra tooltip encima del cursor al pasar sobre .state
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

  // Evento de clic sobre cualquier figura
  contenido.selectAll("path, rect, circle").on("click", function (event) {
    zoomToElement(this);
  });

  // Reset
  d3.select("#resetButton").on("click", () => {
    svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
  });

  const container = document.querySelector(".map-container");
  const tooltip = document.getElementById("tooltip");
  const states = document.querySelectorAll("#mapSvg .state");

  if (!container || !tooltip || states.length === 0) {
    // Si no hay estados, aún así evitamos errores
    console.warn(
      'Mapa o estados no encontrados. Asegúrate de que el SVG tenga elementos con class="state".'
    );
  }

  // funciones para generar el degradado de tres colores
  function interpolateColor(color1, color2, factor) {
    const c1 = color1.match(/\w\w/g).map((c) => parseInt(c, 16));
    const c2 = color2.match(/\w\w/g).map((c) => parseInt(c, 16));
    const result = c1.map((c, i) => Math.round(c + (c2[i] - c) * factor));
    return "#" + result.map((c) => c.toString(16).padStart(2, "0")).join("");
  }

  function generateSemaforoColors() {
    const colors = [];
    const red = "#612332";
    const amber = "#e6d194";
    const green = "#002f2a";

    for (let i = 0; i <= 100; i++) {
      if (i <= 50) {
        const factor = i / 50;
        colors.push(interpolateColor(red, amber, factor));
      } else {
        const factor = (i - 50) / 50;
        colors.push(interpolateColor(amber, green, factor));
      }
    }
    return colors;
  }
  //-----------------------------------------------------------

    // Posición de la barra de colores a la derecha
    const legendX = width - 80;  // 50 px desde el borde derecho
    const legendY = 50;
    const legendWidth = 20;
    const legendHeight = 300;

    // Escala de color en hex
    const colorScaleI = d3.scaleLinear()
      .domain([0, 0.5, 1])
      .range(["#612332", "#e6d194", "#002f2a"]);

    // Dibujar la barra de color vertical con 100 pasos
    const steps = 100;
    const stepHeight = legendHeight / steps;

    for(let i = 0; i < steps; i++) {
      svg.append("rect")
        .attr("x", legendX)
        .attr("y", legendY + i * stepHeight)
        .attr("width", legendWidth)
        .attr("height", stepHeight)
        .attr("fill", colorScaleI(1 - i/(steps-1))); // invertir para que 0% arriba y 100% abajo
    }

    // Etiquetas: 0%, 50%, 100%
    const labels = [
      {text: "100%", y: legendY},  // arriba
      {text: "50%", y: legendY + legendHeight/2}, // medio
      {text: "0%", y: legendY + legendHeight}   // abajo
    ];

    svg.selectAll(".legend-label")
      .data(labels)
      .enter()
      .append("text")
      .attr("x", legendX + legendWidth + 5)
      .attr("y", d => d.y)
      .attr("alignment-baseline", d => {
        if(d.text === "0%") return "hanging";
        if(d.text === "50%") return "middle";
        return "baseline";
      })
      .text(d => d.text);

  //-----------------------------------------------------------

  // funcion prueba para array numeros aleatorios
  const USE_WEIGHTED_AVERAGE = false;

  function obtenerValor(valor) {
    // Si viene como array
    if (Array.isArray(valor)) {
      if (valor.length === 0) return 200;

      // Extraer índices válidos y pesos (si existen)
      const indices = [];
      const pesos = [];

      for (const item of valor) {
        if (item == null) continue;

        // Caso: número directo en el array
        if (typeof item === "number" && !Number.isNaN(item)) {
          indices.push(item);
          pesos.push(1);
          continue;
        }

        // Caso: objeto con 'indice'
        if (typeof item === "object" && "avance" in item) {
          const ind = Number(item.avance);
          if (!Number.isNaN(ind)) {
            indices.push(ind);
            // peso por defecto 1 si no hay 'p'
            const p = "p" in item ? Number(item.p) : 1;
            pesos.push(Number.isFinite(p) && p > 0 ? p : 1);
          }
        }
      }

      if (indices.length === 0) return 200;

      // Promedio ponderado o simple según flag
      if (USE_WEIGHTED_AVERAGE) {
        const totalPeso = pesos.reduce((a, b) => a + b, 0);
        if (totalPeso === 0) return 200;
        const sumaPonderada = indices.reduce(
          (acc, ind, i) => acc + ind * pesos[i],
          0
        );
        return sumaPonderada / totalPeso;
      } else {
        const suma = indices.reduce((a, b) => a + b, 0);
        return suma / indices.length;
      }
    }

    // Si viene como objeto directo {indice: X}
    if (valor && typeof valor === "object") {
      if ("avance" in valor) {
        const ind = Number(valor.indice);
        return Number.isNaN(ind) ? 200 : ind;
      }
      return 200;
    }

    // Si es un número directo
    if (typeof valor === "number" && !Number.isNaN(valor)) return valor;

    // Fallback
    return 200;
  }

  const el = document.getElementById("datos_mapa");
  if (!el)
    return console.error('No se encontró el script con id "datos_mapa".');

  let datos;
  try {
    datos = JSON.parse(el.textContent);
  } catch (err) {
    console.error("Error parseando JSON:", err);
    return;
  }

  const numerosAleatorios = [];

  Object.entries(datos).forEach(([estado, valor]) => {
    const numero = obtenerValor(valor);
    numerosAleatorios.push(numero.toFixed(0));
  });

  // const numerosAleatorios = [];
  // for (let i = 0; i < 32; i++) {
  //   // Genera un número entero entre 0 y 100 (inclusive)
  //   const numero = Math.floor(Math.random() * 101);
  //   numerosAleatorios.push(numero);
  // }
  //-----------------------------------------------------------

  function show(name, clientX, clientY) {
    tooltip.textContent = name;
    tooltip.style.display = "block";
    // calcular posición relativa al contenedor
    const rect = container.getBoundingClientRect();
    const left = clientX - rect.left; // X dentro del contenedor
    const top = clientY - rect.top; // Y dentro del contenedor
    const offsetY = 10; // px por encima del cursor
    tooltip.style.left = `${left}px`;
    tooltip.style.top = `${top - offsetY}px`;
    tooltip.setAttribute("aria-hidden", "false");
  }

  function hide() {
    tooltip.style.display = "none";
    tooltip.setAttribute("aria-hidden", "true");
  }

  // attach listeners
  states.forEach((el, index) => {
    const name =
      el.dataset.name || el.getAttribute("title") || el.id || "Estado";
    el.addEventListener("mouseenter", (e) => {
      show(name, e.clientX, e.clientY);
    });
    el.addEventListener("mousemove", (e) => {
      let avanceT = numerosAleatorios[index % numerosAleatorios.length];
      // console.log(avanceT);
      if (avanceT == 200) {
        show(name + "\nSin visita", e.clientX, e.clientY);
      } else {
        show(name + "\nAvance: " + avanceT + "%", e.clientX, e.clientY);
      }
    });
    el.addEventListener("mouseleave", hide);

    // accessibility: keyboard focus shows tooltip at element centroid
    el.setAttribute("tabindex", "0");
    el.addEventListener("focus", (e) => {
      // calcular centro del elemento en pantalla
      const bbox = el.getBoundingClientRect();
      const cx = bbox.left + bbox.width / 2;
      const cy = bbox.top + bbox.height / 2;
      show(name, cx, cy);
    });
    el.addEventListener("blur", hide);
  });

  // pintar mapa en funcion del % realizado

  const semaforoColors = generateSemaforoColors();
  const mapGroup = document.getElementById("map-data");
  const estados = mapGroup.querySelectorAll("path");

  estados.forEach((estado, index) => {
    let color = "#808080";
    if (numerosAleatorios[index] === 200) {
      color = "#808080";
    } else {
      color = semaforoColors[numerosAleatorios[index % semaforoColors.length]]; // cicla si hay más estados que colores
    }
    // console.log(color);
    estado.style.fill = color;
  });
  //-----------------------------------------------------------

  const modal = document.getElementById("modal");
  const modalTitle = document.getElementById("modalTitle");
  const modalInfo = document.getElementById("modalAvance");
  const closeModal = document.getElementById("closeModal");


  function crearTd(texto) {
    const td = document.createElement("td");
    td.className = "border border-gray-300 px-4 py-2 text-center";
    td.textContent = texto;
    return td;
  }
  function crearTdR(texto) {
    const td = document.createElement("td");
    td.className = "border border-gray-300 px-4 py-2 text-lg text-center font-bold text-inm-rojo-100 bg-[#f3bcd2]";
    td.textContent = texto;
    return td;
  }

  estados.forEach((estado, index) => {
    estado.addEventListener("click", () => {
      // Cancelar cualquier timeout anterior
      clearTimeout(modalTimeout);

      modalTimeout = setTimeout(() => {
        const nombre = estado.getAttribute("title");
        modalTitle.textContent = nombre;

        const avacesOR = numerosAleatorios[index % semaforoColors.length]

        if (avacesOR == 200) {
          modalInfo.textContent =
          "Sin visita";
          document.getElementById("tabla_M").style.display = 'none';
        } else {
          document.getElementById("tabla_M").style.display = 'block';
          modalInfo.textContent =
            "Avance de Seguimiento: " +
            avacesOR +
            "%";
        }
        
        
        const tbody = document.getElementById("mi-tbody");
        tbody.innerHTML = "";

        Object.values(datos)[index].map((items, index2) => {
          if (Array.isArray(items)) {
            // caso: lista de objetos
            items.forEach(item => {
              const tr = document.createElement("tr");
              tr.appendChild(crearTd(index2+1));
              tr.appendChild(crearTd(item.fecha));
              tr.appendChild(crearTd(item.total));
              tr.appendChild(crearTd(item.atendido));
              if (item.pendiente > 0 ){
                tr.appendChild(crearTdR(item.pendiente));
              } else {
                tr.appendChild(crearTd(item.pendiente));
              }
              tr.appendChild(crearTd(item.avance));
              tbody.appendChild(tr);
            });
          } else if (typeof items === "object" && items !== null) {
            // caso: un solo objeto
            console.log(1,items.total, "aten"+items.atendido, items.pendiente)
            const tr = document.createElement("tr");
            tr.appendChild(crearTd(1));
            tr.appendChild(crearTd(items.fecha));
            tr.appendChild(crearTd(items.total));
            tr.appendChild(crearTd(items.atendido));
            if (items.pendiente > 0 ){
                tr.appendChild(crearTdR(items.pendiente));
            } else {
                tr.appendChild(crearTd(items.pendiente));
            }
            tr.appendChild(crearTd(items.avance));
            tbody.appendChild(tr);
          }
        });
        modal.style.display = "block";
      }, 750);
    });
  });

  // cerrar modal con la X
  closeModal.addEventListener("click", () => {
    clearTimeout(modalTimeout); // evita que se abra si se cerró antes
    //regresar zoom original
    svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
    modal.style.display = "none";
  });

  // cerrar si se da clic fuera del contenido
  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      clearTimeout(modalTimeout);
      modal.style.display = "none";
    }
  });
});

// if (Array.isArray(items) && items.length > 0) {
          //   console.log(items);
          //   items.forEach( item => {
          //     const tr = document.createElement("tr");
          //     tr.appendChild(crearTd(item.fecha));
          //     tr.appendChild(crearTd(item.total));
          //     tr.appendChild(crearTd(item.pendiente));
          //     tr.appendChild(crearTd(item.atendido));
          //     tr.appendChild(crearTd(item.avance));
          //     // // Crear celda
          //     // const td = document.createElement("td");
          //     // td.className = "bg-gray-500 border border-gray-300 text-sm px-2 py-2 text-center";
          //     // td.textContent = "Dato 1";
          //     // // Agregar celda a la fila
          //     // tr.appendChild(td);
          //     // Agregar fila al tbody
          //     tbody.appendChild(tr);
          //   });
