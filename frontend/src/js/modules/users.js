/**
 * users.js — Módulo de gestión de usuarios
 *
 * Funcionalidades:
 * - Búsqueda en tiempo real por nombre o email (filtra la tabla sin recargar).
 * - Filtro por estado (Todos / Activos / Inactivos).
 * - Confirmación de eliminación con modal nativo mejorado.
 * - Indicador visual en el botón submit durante el envío de formularios.
 */


// ---------------------------------------------------------------------------
// Búsqueda en tiempo real
// ---------------------------------------------------------------------------

/**
 * Inicializa la búsqueda en tiempo real sobre la tabla de usuarios.
 * Filtra filas por nombre o email al escribir en el input de búsqueda.
 *
 * @param {string} inputId   - ID del input de búsqueda.
 * @param {string} tableBodyId - ID del tbody de la tabla.
 */
function initUserSearch(inputId, tableBodyId) {
    const input = document.getElementById(inputId);
    const tbody = document.getElementById(tableBodyId);

    if (!input || !tbody) return;

    input.addEventListener("input", () => {
        const query = input.value.trim().toLowerCase();
        const rows = tbody.querySelectorAll("tr");

        let visibleCount = 0;

        rows.forEach(row => {
            // Buscar en nombre (col 0) y email (col 1)
            const name  = row.cells[0]?.textContent.toLowerCase() ?? "";
            const email = row.cells[1]?.textContent.toLowerCase() ?? "";

            const matches = name.includes(query) || email.includes(query);
            row.style.display = matches ? "" : "none";
            if (matches) visibleCount++;
        });

        // Mostrar mensaje si no hay resultados
        updateEmptyState(tbody, visibleCount, query);
    });
}


// ---------------------------------------------------------------------------
// Filtro por estado
// ---------------------------------------------------------------------------

/**
 * Inicializa los botones de filtro por estado (Todos / Activos / Inactivos).
 *
 * @param {string} filterContainerId - ID del contenedor con los botones de filtro.
 * @param {string} tableBodyId       - ID del tbody de la tabla.
 */
function initStatusFilter(filterContainerId, tableBodyId) {
    const container = document.getElementById(filterContainerId);
    const tbody     = document.getElementById(tableBodyId);

    if (!container || !tbody) return;

    const buttons = container.querySelectorAll("[data-filter]");

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            const filter = btn.dataset.filter; // "all" | "active" | "inactive"

            // Estilo activo en el botón seleccionado
            buttons.forEach(b => {
                b.classList.remove("bg-indigo-600", "text-white");
                b.classList.add("bg-white", "text-gray-600", "border", "border-gray-300");
            });
            btn.classList.add("bg-indigo-600", "text-white");
            btn.classList.remove("bg-white", "text-gray-600", "border", "border-gray-300");

            // Filtrar filas
            const rows = tbody.querySelectorAll("tr");
            let visibleCount = 0;

            rows.forEach(row => {
                const badge = row.querySelector("[data-status]");
                if (!badge) return;

                const status = badge.dataset.status; // "active" | "inactive"
                const show   = filter === "all" || status === filter;

                row.style.display = show ? "" : "none";
                if (show) visibleCount++;
            });

            updateEmptyState(tbody, visibleCount, "");
        });
    });
}


// ---------------------------------------------------------------------------
// Estado vacío
// ---------------------------------------------------------------------------

/**
 * Muestra u oculta una fila de "sin resultados" en la tabla.
 */
function updateEmptyState(tbody, visibleCount, query) {
    let emptyRow = tbody.querySelector(".empty-state-row");

    if (visibleCount === 0) {
        if (!emptyRow) {
            emptyRow = document.createElement("tr");
            emptyRow.className = "empty-state-row";
            emptyRow.innerHTML = `
                <td colspan="5" class="px-6 py-10 text-center text-gray-400 text-sm">
                    ${query
                        ? `No se encontraron usuarios para "<strong>${query}</strong>".`
                        : "No hay usuarios que coincidan con el filtro."}
                </td>`;
            tbody.appendChild(emptyRow);
        }
    } else {
        emptyRow?.remove();
    }
}


// ---------------------------------------------------------------------------
// Submit con indicador de carga
// ---------------------------------------------------------------------------

/**
 * Agrega un indicador visual al botón submit mientras el formulario se envía.
 * Previene doble envío.
 *
 * @param {string} formId      - ID del formulario.
 * @param {string} submitLabel - Texto del botón mientras carga. Ej: "Guardando..."
 */
function initFormSubmitLoader(formId, submitLabel = "Guardando...") {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener("submit", () => {
        const btn = form.querySelector("[type=submit]");
        if (!btn) return;

        btn.disabled = true;
        btn.textContent = submitLabel;
        btn.classList.add("opacity-75", "cursor-not-allowed");
    });
}


// ---------------------------------------------------------------------------
// Init — punto de entrada
// ---------------------------------------------------------------------------

/**
 * Inicializa todos los comportamientos del módulo de usuarios.
 * Se llama desde el template con: UsersModule.init()
 */
function init() {
    initUserSearch("user-search", "users-tbody");
    initStatusFilter("status-filter", "users-tbody");
    initFormSubmitLoader("user-form");
}

// Exportar como objeto global para uso desde templates Jinja
window.UsersModule = { init };