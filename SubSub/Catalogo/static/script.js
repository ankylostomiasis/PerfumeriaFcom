const $ = (selector, context = document) => context.querySelector(selector);

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (const rawCookie of cookies) {
            const cookie = rawCookie.trim();
            if (cookie.startsWith(`${name}=`)) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    }[char]));
}

function showMessage(message, type = "info", timeout = 2400) {
    let container = $("#toast-container");

    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        Object.assign(container.style, {
            position: "fixed",
            top: "18px",
            right: "18px",
            zIndex: "2000",
            display: "grid",
            gap: "10px",
            maxWidth: "calc(100vw - 36px)",
        });
        document.body.appendChild(container);
    }

    const backgrounds = {
        success: "linear-gradient(135deg, #0f1723, #304563)",
        error: "linear-gradient(135deg, #6f1d1b, #b91c1c)",
        info: "linear-gradient(135deg, #223149, #c89a45)",
    };

    const toast = document.createElement("div");
    Object.assign(toast.style, {
        background: backgrounds[type] || backgrounds.info,
        color: "#ffffff",
        padding: "12px 16px",
        borderRadius: "18px",
        boxShadow: "0 18px 40px rgba(15,23,42,.18)",
        fontWeight: "700",
        fontSize: "0.94rem",
        opacity: "0",
        transform: "translateY(-8px)",
        transition: "opacity .25s ease, transform .25s ease",
    });

    toast.textContent = message;
    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.opacity = "1";
        toast.style.transform = "translateY(0)";
    });

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-8px)";
    }, timeout - 250);

    setTimeout(() => toast.remove(), timeout);
}

function cartItemMarkup(item) {
    const name = escapeHtml(item.name);
    const quantity = Number(item.quantity) || 0;
    const total = Number(item.total_price) || 0;
    const productId = Number(item.id);

    const thumb = item.picture_url
        ? `<img src="${item.picture_url}" alt="${name}" class="cart-item-image">`
        : `<div class="cart-thumb-placeholder"><i class="bi bi-stars"></i></div>`;

    return `
        <li class="list-group-item cart-item">
            <div class="cart-thumb">
                ${thumb}
            </div>

            <div class="cart-item-main">
                <strong class="cart-item-title">${name}</strong>
                <span class="cart-item-meta">Detalle listo para confirmar</span>

                <div class="cart-qty-controls">
                    <button class="btn qty-btn" type="button" onclick="decreaseQuantity(${productId})" aria-label="Reducir cantidad">
                        <i class="bi bi-dash-lg"></i>
                    </button>
                    <span class="qty-value">${quantity}</span>
                    <button class="btn qty-btn" type="button" onclick="increaseQuantity(${productId})" aria-label="Aumentar cantidad">
                        <i class="bi bi-plus-lg"></i>
                    </button>
                </div>
            </div>

            <div class="cart-item-side">
                <span class="cart-price">$${total.toFixed(2)}</span>
                <button class="btn remove-btn" type="button" onclick="removeFromCart(${productId})" aria-label="Eliminar producto">
                    <i class="bi bi-x-lg"></i>
                </button>
            </div>
        </li>
    `;
}

function cartEmptyMarkup() {
    return `
        <li class="list-group-item cart-empty-state">
            <i class="bi bi-bag-heart"></i>
            <span>Tu carrito esta vacio por ahora.</span>
        </li>
    `;
}

async function updateCartUI(data = null) {
    const list = $("#cart-items");
    const totalElement = $("#cart-total");
    const countElement = $("#cart-count");

    if (!list || !totalElement || !countElement) {
        return;
    }

    if (!data) {
        try {
            const response = await fetch("/view_cart/", {
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            });
            data = await response.json();
        } catch (error) {
            console.error("No se pudo actualizar el carrito", error);
            return;
        }
    }

    const items = Array.isArray(data.cart_items) ? data.cart_items : [];
    const total = Number(data.cart_total_price) || 0;
    const count = Number(data.cart_total_quantity) || 0;

    list.innerHTML = items.length ? items.map(cartItemMarkup).join("") : cartEmptyMarkup();
    totalElement.textContent = `$${total.toFixed(2)}`;
    countElement.textContent = String(count);
}

async function requestCartUpdate(url, options, successMessage, errorMessage) {
    try {
        const response = await fetch(url, options);
        const data = await response.json();

        if (data.status === "success") {
            await updateCartUI(data);
            if (successMessage) {
                showMessage(successMessage, "success");
            }
            return;
        }

        showMessage(data.message || errorMessage, "error");
        return;
    } catch (error) {
        console.error(errorMessage, error);
    }

    showMessage(errorMessage, "error");
}

window.addToCart = async function addToCart(productId) {
    await requestCartUpdate(
        `/add_to_cart/${productId}/`,
        {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),
            },
        },
        "Fragancia agregada al carrito",
        "No se pudo agregar el producto"
    );
};

window.removeFromCart = async function removeFromCart(productId) {
    await requestCartUpdate(
        `/remove_from_cart/${productId}/`,
        {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "X-Requested-With": "XMLHttpRequest",
            },
        },
        "Producto retirado del carrito",
        "No se pudo actualizar el carrito"
    );
};

window.increaseQuantity = function increaseQuantity(productId) {
    window.addToCart(productId);
};

window.decreaseQuantity = async function decreaseQuantity(productId) {
    await requestCartUpdate(
        `/decrease_quantity/${productId}/`,
        {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "X-Requested-With": "XMLHttpRequest",
            },
        },
        "Cantidad actualizada",
        "No se pudo reducir la cantidad"
    );
};

window.verProducto = function verProducto(productRef) {
    if (typeof productRef === "string" && productRef.length > 0) {
        window.location.href = productRef;
        return;
    }

    window.location.href = `/product/${productRef}/`;
};

function productCardMarkup(product, label = "") {
    const hasPicture = Boolean(product.picture_url);
    const picture = hasPicture
        ? `<img src="${product.picture_url}" alt="${escapeHtml(product.name)}" class="card-img-top">`
        : `<div class="product-placeholder"><i class="bi bi-stars"></i></div>`;
    const price = Number(product.price) || 0;
    const name = escapeHtml(product.name);
    const description = escapeHtml(product.description || "");
    const badge = label ? `<span>${escapeHtml(label)}</span>` : `<span>${escapeHtml(product.category || "Fragancia")}</span>`;
    const detailUrl = product.detail_url || `/product/${product.id}/`;
    const inStock = Number(product.stock) > 0;

    const action = inStock
        ? `<button type="button" class="btn action-btn action-btn-outline action-btn-sm" onclick="event.stopPropagation(); addToCart(${product.id})">Agregar</button>`
        : `<a href="/ask_for_stock/?product_id=${product.id}" class="btn action-btn action-btn-outline action-btn-sm" onclick="event.stopPropagation();">Consultar</a>`;

    const availability = inStock
        ? `<span class="badge-available">Disponible</span>`
        : `<span class="badge-soldout">Agotado</span>`;

    return `
        <div class="col-6 col-md-4 col-lg-3">
            <article class="product-card grid-product-card" onclick="verProducto('${detailUrl}')">
                <div class="product-media">
                    ${picture}
                </div>

                <div class="product-body">
                    <div class="product-badges">
                        ${badge}
                        ${availability}
                    </div>
                    <h3>${name}</h3>
                    <p class="product-description">${description}</p>
                    <div class="product-footer">
                        <span class="product-price">$${price.toFixed(2)}</span>
                        ${action}
                    </div>
                </div>
            </article>
        </div>
    `;
}

window.cargarCategoria = async function cargarCategoria(categoriaId) {
    const container = $("#product-container");

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="col-12">
            <div class="empty-state">
                <div class="spinner-border" style="color:#304563" role="status"></div>
                <p>Cargando productos de la categoria...</p>
            </div>
        </div>
    `;

    try {
        const response = await fetch(`/categoria/${categoriaId}/`, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        });
        const data = await response.json();

        if (!Array.isArray(data.productos) || !data.productos.length) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="empty-state">
                        <i class="bi bi-box"></i>
                        <p>No encontramos productos en <strong>${escapeHtml(data.categoria || "esta categoria")}</strong>.</p>
                    </div>
                </div>
            `;
            return;
        }

        const heading = `
            <div class="col-12">
                <div class="section-heading section-heading-tight">
                    <div>
                        <span class="section-eyebrow">Categoria activa</span>
                        <h2 class="section-title">${escapeHtml(data.categoria)}</h2>
                    </div>
                    <p class="section-copy">Estas son las opciones disponibles para mostrarle al cliente ahora mismo.</p>
                </div>
            </div>
        `;

        const cards = data.productos.map((product) => productCardMarkup(product)).join("");
        container.innerHTML = heading + cards;
        container.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
        console.error("No se pudo cargar la categoria", error);
        container.innerHTML = `
            <div class="col-12">
                <div class="empty-state">
                    <i class="bi bi-exclamation-circle"></i>
                    <p>Hubo un problema cargando la categoria. Intenta de nuevo.</p>
                </div>
            </div>
        `;
    }
};

function debounce(callback, delay = 280) {
    let timeoutId;

    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => callback(...args), delay);
    };
}

function defaultSearchPanelMarkup() {
    return `
        <div class="col-12">
            <div class="empty-state">
                <i class="bi bi-hand-index-thumb"></i>
                <p>Selecciona una categoria para ver sus productos aqui mismo.</p>
            </div>
        </div>
    `;
}

function setupLiveSearch() {
    const searchBar = $("#search-bar");
    const productContainer = $("#product-container");

    if (!searchBar || !productContainer) {
        return;
    }

    const runSearch = debounce(async () => {
        const query = searchBar.value.trim();

        if (query.length === 0) {
            productContainer.innerHTML = defaultSearchPanelMarkup();
            return;
        }

        if (query.length < 2) {
            productContainer.innerHTML = `
                <div class="col-12">
                    <div class="empty-state">
                        <i class="bi bi-search"></i>
                        <p>Escribe al menos dos letras para filtrar sin salir del inicio.</p>
                    </div>
                </div>
            `;
            return;
        }

        try {
            const response = await fetch(`/search/?q=${encodeURIComponent(query)}`, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            });
            const products = await response.json();

            if (!Array.isArray(products) || !products.length) {
                productContainer.innerHTML = `
                    <div class="col-12">
                        <div class="empty-state">
                            <i class="bi bi-search"></i>
                            <p>No encontramos resultados para <strong>${escapeHtml(query)}</strong>.</p>
                        </div>
                    </div>
                `;
                return;
            }

            const heading = `
                <div class="col-12">
                    <div class="section-heading section-heading-tight">
                        <div>
                            <span class="section-eyebrow">Busqueda rapida</span>
                            <h2 class="section-title">Resultados para "${escapeHtml(query)}"</h2>
                        </div>
                        <p class="section-copy">Coincidencias encontradas sin salir del inicio.</p>
                    </div>
                </div>
            `;

            const cards = products.map((product) => productCardMarkup(product, "Busqueda")).join("");
            productContainer.innerHTML = heading + cards;
        } catch (error) {
            console.error("No se pudo ejecutar la busqueda", error);
        }
    });

    searchBar.addEventListener("input", runSearch);
}

function setupCarousel(trackId, prevId, nextId) {
    const track = document.getElementById(trackId);
    const prevButton = document.getElementById(prevId);
    const nextButton = document.getElementById(nextId);

    if (!track || !prevButton || !nextButton) {
        return;
    }

    let pointerDown = false;
    let startX = 0;
    let startScrollLeft = 0;
    let dragged = false;
    let suppressClick = false;
    let activePointerId = null;

    const dragThreshold = 10;

    const getStep = () => {
        const firstItem = track.firstElementChild;

        if (!firstItem) {
            return track.clientWidth * 0.85;
        }

        const gap = parseInt(window.getComputedStyle(track).gap || "0", 10);

        return firstItem.getBoundingClientRect().width + gap;
    };

    const updateButtons = () => {
        const maxScroll = Math.max(track.scrollWidth - track.clientWidth, 0);

        prevButton.disabled = track.scrollLeft <= 4;
        nextButton.disabled = track.scrollLeft >= maxScroll - 4;
    };

    const endDrag = () => {
        if (!pointerDown) return;

        pointerDown = false;
        track.classList.remove("is-dragging");

        if (activePointerId !== null) {
            track.releasePointerCapture?.(activePointerId);
        }

        activePointerId = null;

        if (dragged) {
            suppressClick = true;

            setTimeout(() => {
                suppressClick = false;
            }, 180);
        } else {
            suppressClick = false;
        }

        dragged = false;
    };

    prevButton.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();

    track.scrollLeft -= getStep();
});

nextButton.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();

    track.scrollLeft += getStep();
});

    track.addEventListener("pointerdown", (event) => {
        if (event.pointerType !== "touch" && event.button !== 0) {
            return;
        }

        if (event.target.closest("button, a")) {
            return;
        }

        pointerDown = true;
        dragged = false;
        suppressClick = false;

        startX = event.clientX;
        startScrollLeft = track.scrollLeft;
        activePointerId = event.pointerId;

        track.classList.add("is-dragging");
        track.setPointerCapture?.(event.pointerId);
    });

    track.addEventListener("pointermove", (event) => {
        if (!pointerDown) return;

        const delta = event.clientX - startX;

        if (Math.abs(delta) > dragThreshold) {
            dragged = true;
        }

        track.scrollLeft = startScrollLeft - delta;
    });

    track.addEventListener("pointerup", endDrag);
    track.addEventListener("pointercancel", endDrag);
    track.addEventListener("lostpointercapture", endDrag);

    track.addEventListener(
        "click",
        (event) => {
            if (!suppressClick) return;

            event.preventDefault();
            event.stopPropagation();
        },
        true
    );

    track.addEventListener("scroll", updateButtons, { passive: true });
    window.addEventListener("resize", updateButtons);

    updateButtons();
}
function setupRevealAnimations() {
    const elements = document.querySelectorAll("[data-reveal]");

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-visible");
                obs.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0
    });

    elements.forEach(el => {
        observer.observe(el);

        // 💡 FIX CRÍTICO: si ya está visible al cargar
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight) {
            el.classList.add("is-visible");
            observer.unobserve(el);
        }
    });
}

function setupOffcanvasCartRefresh() {
    const offcanvasCart = document.getElementById("offcanvasCart");

    if (!offcanvasCart) {
        return;
    }

    offcanvasCart.addEventListener("show.bs.offcanvas", () => {
        updateCartUI();
    });
}

function setupCheckoutGuard() {
    const checkoutButton = document.getElementById("btn-pago");

    if (!checkoutButton) {
        return;
    }

    checkoutButton.addEventListener("click", (event) => {
        const count = Number.parseInt($("#cart-count")?.textContent || "0", 10) || 0;

        if (count > 0) {
            return;
        }

        event.preventDefault();
        showMessage("Tu carrito esta vacio. Agrega al menos una fragancia antes de continuar a WhatsApp.", "info", 3200);
    });
}
document.addEventListener("DOMContentLoaded", () => {
    setupRevealAnimations();

    // 👇 INICIALIZAR CAROUSELS
    setupCarousel("category-carousel", "prev-cat", "next-cat");
    setupCarousel("products-carousel", "prev-prod", "next-prod");
});
document.querySelectorAll(".carousel-shell").forEach(shell => {
    const track = shell.querySelector(".carousel-track");
    const cards = track.children;

    const prevBtn = shell.querySelector(".prev-btn");
    const nextBtn = shell.querySelector(".next-btn");

    let index = 0;

    function scrollToCard(i) {
        if (i < 0) i = 0;
        if (i >= cards.length) i = cards.length - 1;

        index = i;

        cards[index].scrollIntoView({
            behavior: "smooth",
            inline: "start",
            block: "nearest"
        });
    }

    nextBtn.addEventListener("click", () => {
        scrollToCard(index + 1);
    });

    prevBtn.addEventListener("click", () => {
        scrollToCard(index - 1);
    });
});